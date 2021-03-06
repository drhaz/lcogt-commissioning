# lcogt-commissioning
Software for use in astronomical commissioning of instruments on the LCOGT network

Updated by Daniel Harbeck:
==
The original scripts provided by Rachel Street were tuned for the old 3D cube fits format
 of the LCO Sinistro cameras. Since the original commissioning of the Sinsitro cameras, the storage
 format was revised and now uses a MEF format.For continued commissioning and reverification of the
 LCO cameras, these tools are being rewritten by Daniel Harbeck to be compatible with the new format. 

 Note: The scripts explained below are updated; scripts not mentioned here have not been vetted yet and 
 is vestigial code 

noisegainmef.py
===

Measure read noise [e-] and gain [e-/ADU]  based on a pair of raw biases images and equally exposed
flat field images. If more than one pair of flat fields are given, they are matched either by exposure time 
or illumination level (user selectable).  

Syntax is:
<pre>
(venv) dharbeck@dharbeck-lco2:~/Software/lcogt-commissioning/scripts$ python noisegainrawmef.py -h
usage: noisegainrawmef.py [-h] [--minx MINX] [--maxx MAXX] [--miny MINY]
                          [--maxy MAXY] [--imagepath OPT_IMAGEPATH]
                          [--database DATABASE]
                          [--sortby {exptime,filterlevel}] [--noreprocessing]
                          [--loglevel {DEBUG,INFO,WARN}] [--showimages]
                          [--makepng]
                          fitsfile [fitsfile ...]

General purpose CCD noise and gain measurement from pairs of flat fields and
biases.

positional arguments:
  fitsfile              Input fits files, must include at least two bias and
                        two flat field frames.

optional arguments:
  -h, --help            show this help message and exit
  --imagepath OPT_IMAGEPATH
                        pathname to prepend to fits file names. (default:
                        None)
  --database DATABASE   sqlite database where to store results. (default:
                        noisegain.sqlite)
  --sortby {exptime,filterlevel}
                        Automatically group flat fiel;ds by exposure time
                        (great if using dome flas, or lab flats)., or by
                        measured light level (great when using sky flats, but
                        more computing intensive (default: exptime)
  --noreprocessing      Do not reprocess if datra are already in database
                        (default: False)
  --loglevel {DEBUG,INFO,WARN}
                        Set the debug level (default: INFO)
  --showimages          Interactively show difference flat and bias images.
                        (default: False)
  --makepng             Create a png output image of noise, gain, and ptc.
                        (default: False)

Optionally, specify the location of statistics window. All units in pixels with an FITS image extension:
  --minx MINX           minimum x. (default: None)
  --maxx MAXX           maximum x. (default: None)
  --miny MINY           miniumm y. (default: None)
  --maxy MAXY           maximum y. (default: None)
</pre>

The fitsfiles are to be in the order: bias1, bias2, flat1, flat2

Example:
<pre>
python noisegainrawmef.py --imagepath /nfs/archive/engineering/cpt/fl14/20170912/raw/ cpt1m013-fl14-20170912-0002-b00.fits.fz cpt1m013-fl14-20170912-0003-b00.fits.fz   cpt1m013-fl14-20170912-0030-f00.fits.fz cpt1m013-fl14-20170912-0031-f00.fits.fz
</pre>


crosstalk.py
====
Measure the crosstalk between amplifiers in a MEF file. 

Updated command line parsing to use argparse. Updated fits reading to properly handle .fz
 compressed fits files. 

Usage example:
<pre>

python crosstalk.py --quadrant 2 --linear --imagepath /nfs/archive/engineering/cpt/fl14/20170913/raw    cpt1m013-fl14-20170913-0106-x00.fits.fz cpt1m013-fl14-20170913-0107-x00.fits.fz cpt1m013-fl14-20170913-0108-x00.fits.fz
</pre>

Paramters:

--quadrant [N] parameter defines which extension number (start counting at 0 ) is considered the contaminating quadrant.
  When loading a raw image in ds9 with the -mosaicimage iraf option, this is where the quadrants are:
<pre>  
       4|3
       -+- 
       1|2
</pre>
  the input parameter needs those quadrant ids -1 (should change code one day though!)

--linear will determine linear crosstalk relation

--imagepath [path]  points to the directory where images located and will be prepended to the
 following individual image names. Save a bit of repetitive typing of the same path.

The following fits images wil be analysed for cross talk. While the software was written with the 
LCO Sinistro cameras in mind, the current version o this script should work with any camera as 
long as the output of amplifiers is stored in equally dimensioned fits extensions. 


submitXtalkObs.py
===

X-Talk calibration submission tool Submit to POND the request to observe a
bright star, defocussed, at 1,3,6,12 sec exposure time, on each quadrant.

<pre>
(venv) dharbeck@dharbeck-lco2:~/Software/lcogt-commissioning/scripts$ python ./submitXtalkObservation.py -h
usage: submitXtalkObservation.py [-h] --site {lsc,cpt,coj,elp,bpl} --dome
                                 {doma,domb,domc} [--telescope TELESCOPE]
                                 --instrument
                                 {fl03,fl04,fl05,fl08,fl11,fl12,fl14,fl15,fl16,fa02,fa03,fa04,fa05,fa06,fa08,fa11,fa12,fa14,fa15,fa16}
                                 [--name {auto,91 Aqr,HD30562,15 Sex,30Psc,51Hya}]
                                 [--start START] [--defocus DEFOCUS]
                                 [--user USER] [--offsetRA OFFSETRA]
                                 [--offsetDec OFFSETDEC] [--CONFIRM]
                                 [--loglevel {DEBUG,INFO,WARN}]

X-Talk calibration submission tool Submit to LAKE the request to observe a
bright star, defocussed, at 1,3,6,12 sec exposure time, on each quadrant.
Useful when commissioing a camera that is not available via scheduler yet.

optional arguments:
  -h, --help            show this help message and exit
  --site {lsc,cpt,coj,elp,bpl}
                        To which site to submit
  --dome {doma,domb,domc}
                        To which enclosure to submit
  --telescope TELESCOPE
  --instrument {fl03,fl04,fl05,fl08,fl11,fl12,fl14,fl15,fl16,fa02,fa03,fa04,fa05,fa06,fa08,fa11,fa12,fa14,fa15,fa16}
                        To which instrument to submit
  --name {auto,91 Aqr,HD30562,15 Sex,30Psc,51Hya}
                        Name of star for X talk measurement. Will be resolved
                        via simbad. If resolve failes, program will exit.
                        future version will automatically select a star based
                        on time of observation.
  --start START         Time to start x-talk calibration. If not given,
                        defaults to "NOW". Specify as YYYYMMDD HH:MM
  --defocus DEFOCUS     Amount to defocus star.
  --user USER           Which user name to use for submission
  --offsetRA OFFSETRA   Extra pointing offset to apply R.A.
  --offsetDec OFFSETDEC
                        Extra pointing offset to apply Dec
  --CONFIRM             If set, block will be submitted. If omitted, nothing
                        will be submitted.
  --loglevel {DEBUG,INFO,WARN}
                        Set the debug level

</pre>

An example of an actual submission is like:
<pre>
python submitXtalkObs.py --site coj --instrument fl12 --start "20180124 18:17" --name "15 Sex" --CONFIRM
</pre>



bpm.py
===

Create a BANZAI-compatible bad pixel mask out of a set of bias, dark, and flat field frames.

At the minimum, a set of three bias images have to be given as a parameter. A bpm will be calcualted for each image
 extension based on all bias, dark, and flat iamges given. Images of boas, dark, flat will be median combined before
  analysis.

For biases: All pixels with a value larger than 20 times the varaince in the bias will be flagged as bad.
For darks: All pixels with a value larger than 20 times the varaince in the bias will be flagged as bad.
For flats: All pixels with a vlaues smaller than 20% of the median level wil be flagged as bad.


Pixel values indicate in the bpm > 0 indicate a bad pixel; the coding is as:
0&001 - bad because identified as bad in bias
0&010 - bad because identified as bad in dark
0&100 - bad because identified as bad in flat



Usage: 
<pre> dharbeck@dharbeck-lco2:~/Software/lcogt-commissioning/scripts$ python bpm.py --help
      usage: bpm.py [-h] [--log_level {DEBUG,INFO}]
                    [--outputfilename OUTPUTFILENAME] [--showimages]
                    fitsfiles [fitsfiles ...]
      
      Create a bad pixel mask out of biases, darks, and flat fields
      
      positional arguments:
        fitsfiles             Input FITS files for bpm creation.
      
      optional arguments:
        -h, --help            show this help message and exit
        --log_level {DEBUG,INFO}
                              Set the debug level
        --outputfilename OUTPUTFILENAME
                              Outputfilename
        --showimages          Show bpm of each extension

</pre>

