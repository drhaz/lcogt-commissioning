#!/bin/bash

# Crawls thourgh the LCO archive and attempts to fit gain / readnosie from automatically identified pairs of sky flats
# and daytime biases.
# Edit according to your need below.
# Reqruiements: gnu parallel needs to be installed.



noisegaindatabase="noisegain.sqlite"   # Output database file to store results.
webpageoutputdir="gainhistory"         # existing local subdiretory into which an overview html page will be rendered.


base=/archive/engineering              # Location of archive mount

NCPU=30                                # How many CPUs to employ

time python lcocommissioning/crawl_noisegain.py --ncpu $NCPU --ndays 5 --noreprocessing --loglevel INFO --database ${noisegaindatabase}

time analysgainhistory --outputdir ${webpageoutputdir} --database ${noisegaindatabase}
