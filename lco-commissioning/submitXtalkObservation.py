import argparse
import logging
import ephem
import math
from astropy import units as u
from astropy.coordinates import SkyCoord, Angle
import datetime as dt
import common.common as common

_log = logging.getLogger(__name__)

sinistro_1m_quadrant_offsets = {0: [-450, 450],
                                1: [450, 450],
                                2: [450, -450],
                                3: [-450, -450]}

goodXTalkTargets = ['auto', '91 Aqr', 'HD30562', '15 Sex', '30Psc', '51Hya']


def getAutoCandidate(context):

    if  not common.is_valid_lco_site (context.site):
        _log.error("Site %s is not known. Giving up" % context.site)
        exit(1)

    site = common.getEphemObForSiteAndTime (context.site, context.start + dt.timedelta(minutes=30))
    moon = ephem.Moon()
    moon.compute(site)

    _log.info("Finding suitable star for site %s. Moon phase is  %i %%" % (context.site, moon.moon_phase * 100))

    for starcandidate in goodXTalkTargets:
        if 'auto' in starcandidate:
            continue
        radec = SkyCoord.from_name(starcandidate)
        s = ephem.FixedBody()
        s._ra = radec.ra.degree * math.pi / 180
        s._dec = radec.dec.degree * math.pi / 180
        s.compute(site)

        moonseparation = (ephem.separation((moon.ra, moon.dec), (s.ra, s.dec)))

        alt = s.alt * 180 / math.pi
        moonseparation = moonseparation * 180 / math.pi

        altok = alt > 35
        sepok = moonseparation > 30

        if (altok and sepok):
            print("\nViable star found: %s altitude % 4f moon separation % 4f" % (starcandidate, alt, moonseparation))
            return starcandidate
        else:
            print("rejecting star %s - altitude ok: %s     moon separation ok: %s" % (starcandidate, altok, sepok))

    print("No viable star was found! full moon? giving up!")
    exit(1)


def getRADecForQuadrant(starcoo, quadrant, extraoffsetra=0, extraoffsetDec=0):
    dra = Angle(sinistro_1m_quadrant_offsets[quadrant][0], unit=u.arcsec)
    ddec = Angle(sinistro_1m_quadrant_offsets[quadrant][1], unit=u.arcsec)

    return SkyCoord(starcoo.ra - dra + Angle(extraoffsetra, unit=u.arcsec),
                    starcoo.dec - ddec + Angle(extraoffsetDec, unit=u.arcsec))


def createRequestsForStar(context):
    timePerQuadrant = 8  # in minutes
    absolutestart = context.start

    # create one block per quadrant
    for quadrant in sinistro_1m_quadrant_offsets:

        start = absolutestart + dt.timedelta(minutes=(quadrant) * timePerQuadrant)
        end = start + dt.timedelta(minutes=timePerQuadrant)
        start = str(start).replace(' ', 'T')
        end = str(end).replace(' ', 'T')

        print("Block for %s Q %d from %s to %s" % (context.name, quadrant, str(start), str(end)))

        block_params = {
            "molecules": [],
            'start': start,
            'end': end,
            'site': context.site,
            'observatory': context.dome,
            'telescope': context.telescope,
            'instrument_class': '1m0-SciCam-Sinistro'.upper(),
            'priority': 30,
        }

        offsetPointing = getRADecForQuadrant(context.radec, quadrant, context.offsetRA, context.offsetDec)

        for exptime in [2, 4, 6, 12]:
            moleculeargs = {
                'inst_name': context.instrument,
                'bin': 1,
                'exposure_time': exptime,
                'exposure_count': 1,
                'bin_x': 1,
                'bin_y': 2,

                'filter': 'rp',
                'pointing': {"type": "SP",
                             "name": "%s x talk q %d" % (context.name, quadrant),
                             "coord_type": "RD",
                             "coord_sys": "ICRS",
                             "epoch": "2000",
                             "equinox": "2000",
                             "ra": "%10f" % offsetPointing.ra.degree,
                             "dec": "%7f" % offsetPointing.dec.degree,
                             },

                'group': 'Sinistro x talk commissioning',
                'user_id': context.user,
                'prop_id': 'calibration',
                'defocus': context.defocus,
                'type': 'EXPOSE'
            }

            block_params['molecules'].append(moleculeargs)

        common.send_to_lake(block_params, args.opt_confirmed)


def parseCommandLine():
    parser = argparse.ArgumentParser(
        description='X-Talk calibration submission tool\nSubmit to LAKE the request to observe a bright star, '
                    'defocussed, at 1,3,6,12 sec exposure time, on each quadrant. Useful when commissioing a camera '
                    'that is not available via scheduler yet.')

    parser.add_argument('--site', required=True, choices=['lsc', 'cpt', 'coj', 'elp', 'bpl'],
                        help="To which site to submit")
    parser.add_argument('--dome', required=True, choices=['doma', 'domb', 'domc'], help="To which enclosure to submit")
    parser.add_argument('--telescope', default='1m0a')
    parser.add_argument('--instrument', required=True,
                        choices=['fa02', 'fa03', 'fa04', 'fa05', 'fa06', 'fa08', 'fa11', 'fa12', 'fa14', 'fa15',
                                 'fa16', ],
                        help="To which instrument to submit")
    parser.add_argument('--name', default='auto', type=str, choices=goodXTalkTargets,
                        help='Name of star for X talk measurement. Will be resolved via simbad. If resolve failes, '
                             'program will exit.\n future version will automatically select a star based on time of'
                             ' observation.')
    parser.add_argument('--start', default=None,
                        help="Time to start x-talk calibration. If not given, defaults to \"NOW\". Specify as YYYYMMDD HH:MM")

    parser.add_argument('--defocus', type=float, default=6.0, help="Amount to defocus star.")
    parser.add_argument('--user', default='daniel_harbeck', help="Which user name to use for submission")
    parser.add_argument('--offsetRA', default=0, help="Extra pointing offset to apply R.A.")
    parser.add_argument('--offsetDec', default=0, help="Extra pointing offset to apply Dec")

    parser.add_argument('--CONFIRM', dest='opt_confirmed', action='store_true',
                        help='If set, block will be submitted. If omitted, nothing will be submitted.')

    parser.add_argument('--loglevel', dest='log_level', default='INFO', choices=['DEBUG', 'INFO', 'WARN'],
                        help='Set the debug level')

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(asctime)s.%(msecs).03d %(levelname)7s: %(module)20s: %(message)s')

    if args.start is None:
        args.start = dt.datetime.utcnow()
    else:
        try:
            args.start = dt.datetime.strptime(args.start, "%Y%m%d %H:%M")
        except ValueError:
            _log.error("Invalidt start time argument: ", args.start)
            exit(1)

    if ('auto' in args.name):
        # automatically find the best target
        args.name = getAutoCandidate(args)
        pass

    try:
        _log.debug("Resolving target name")
        args.radec = SkyCoord.from_name(args.name)
    except:
        print("Resolving target name failed, giving up")
        exit(1)

    print("Resolved target %s at corodinates %s %s" % (args.name, args.radec.ra, args.radec.dec))
    return args

def main():
    args = parseCommandLine()
    createRequestsForStar(args)

if __name__ == '__main__':
    main()
