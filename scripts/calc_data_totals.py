# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 10:07:43 2016

@author: rstreet
"""

from os import path
from sys import argv
import glob
import data_counter

def calc_nightly_data_totals(night_dir):
    """Function to calculate the number of frames of different types available
    within a single nights data directory
    """
    data = data_counter.DataCounter()
    frame_list = glob.glob( path.join( night_dir, '*.fits.fz' ) )
    for frame in frame_list:
        if '-b00' in frame:
            data.nbiases = data.nbiases + 1
        elif '-d00' in frame:
            data.ndarks = data.ndarks + 1
        elif '-f00' in frame:
            data.nflats = data.nflats + 1
        elif '-e00' in frame:
            data.nscience = data.nscience + 1
    return data
    
def calc_data_totals():
    """Function to calculate the total number of frames of different types
    acquired within a given time frame"""
    
    params = parse_args_data()

    data = data_counter.DataCounter()
    nframes = 0

    dir_sort = params['dir_list']
    dir_sort.sort()
    
    for night_dir in dir_sort:
        night = night_dir.split('/')[-2]
        night_data = calc_nightly_data_totals(night_dir)
        print night+' '+night_data.summary()
        for ftype in ['nbiases','ndarks','nflats','nscience']:
            fcount = getattr(night_data,ftype)
            setattr(data,ftype,(getattr(data,ftype) + fcount))
            nframes = nframes + fcount

    print('\nData holdings: ')
    print data.summary()
    print('\nTotal number of frames: '+str(nframes))

def parse_args_data():
    """Function to harvest the parameters required for the data summary code
    from the commandline or prompts"""
    
    params = {}
    if len(argv) != 3:
        params['top_data_dir'] = raw_input('Please enter the path to the data directory: ')
        params['date_search_string'] = raw_input('Please enter the date search string [e.g. yyyymmd?]: ')
    else:
        params['top_data_dir'] = argv[1]
        params['date_search_string'] = argv[2]
    
    dir_list = glob.glob(path.join(params['top_data_dir'], \
                                params['date_search_string']))
    params['dir_list'] = []
    for data_dir in dir_list:
        params['dir_list'].append( path.join(data_dir,'raw') )
        
    return params

if __name__ == '__main__':
    calc_data_totals()