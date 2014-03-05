# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 08:56:34 2014

@author: Lukasz Tracewski

Module for parsing user input
"""

import os
import argparse
from collections import namedtuple

AppConfig = namedtuple('AppConfig', ['data_store', 'bucket', 'no_processes', 'write_stdout', 
                                     'delete_data', 'with_spectrogram', 'synchronous', 
                                     'program_directory', 'mail'])

class Configurator(object):
    
    def __init__(self):
        self._parser = argparse.ArgumentParser(description='Automatic identification of kiwi calls from audio recordings',
                                prog='Ornithokrites', epilog='lukasz.tracewski@gmail.com')
        self._parser.add_argument('-b', '--bucket', help='Amazon Web Services S3 bucket name. If not provided '
            'then it is assumed the input data is already available.')
        self._parser.add_argument('-d', '--datastore', help='Directory with recordings. If bucket was '
            'not provided, then program takes this directory as a location of inpiut data. If bucket '
            'was provided, then to this location recordings shall be downloaded.')
        self._parser.add_argument('-m', '--mail', help=argparse.SUPPRESS)
            # help='E-mail address to which a notification will be '
            # 'sent once identification is completed.')               
        self._parser.add_argument('--stdout', help='Print messages to standard output.', action='store_true')
        self._parser.add_argument('--deletedata', help='Keep original data.', action='store_true')
        self._parser.add_argument('--withspectrogram', help='Print spectrogram to a file.', action='store_true')
        group_parallel_proc = self._parser.add_mutually_exclusive_group()
        group_parallel_proc.add_argument('-p', '--numproc', type=int, default=1, help='Number of processes to use.')   
        group_parallel_proc.add_argument('--synchronous', help='Enforce synchronous communication. All the data '
                                          'will be processed on a single thread. Invalidates "numproc" option.', 
                                          action='store_true')
                                          

    def parse_arguments(self):
        args = self._parser.parse_args()
        
        if args.bucket: # Web Interface
            if args.datastore:
                data_store = args.datastore
            else:
                data_store = '/var/www/results/' # default for the Web Interface                
        elif args.datastore: # Command-line batch mode
            data_store = args.datastore     
        self._check_negative(args.numproc)
        program_dir = os.path.dirname(os.path.realpath(__file__))
    
        return AppConfig(data_store, args.bucket, args.numproc, args.stdout, args.deletedata, 
                         args.withspectrogram, args.synchronous, program_dir, args.mail)
        
    def _check_negative(self, value):
        ivalue = int(value)
        if not ivalue > 0:
             raise self._parser.ArgumentTypeError('%s is invalid. Number of processes must be a ' +
                 'positive value.' % value)
        
