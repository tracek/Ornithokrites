# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 08:56:34 2014

@author: Lukasz Tracewski

Module for parsing user input
"""

from collections import namedtuple
from argparse import ArgumentParser

AppConfig = namedtuple('AppConfig', ['data_store', 'bucket', 'write_stdout', 'keep_data'])

class Configurator(object):
    
    def __init__(self):        
        self._parser = ArgumentParser(description='Automatic identification of kiwi calls from audio recordings',
                                prog='Ornithokrites', epilog='lukasz.tracewski@gmail.com')
        self._parser.add_argument('-b', '--bucket', help='Amazon Web Services S3 bucket name')
        self._parser.add_argument('-d', '--datastore', help='Directory to process')
        self._parser.add_argument('--stdout', help='Print messages to standard output', action='store_true')
        self._parser.add_argument('--keep_data', help='Keep original data', action='store_true')
    
    def parse_arguments(self):
        args = self._parser.parse_args()
        
        if args.bucket: # Web Interface
            if args.datastore:
                self.Data_Store = args.datastore
            else:
                self.Data_Store = '/var/www/results/Recordings/' # default for the Web Interface                
        elif args.datastore: # Command-line batch mode
            self.Data_Store = args.datastore        
    
        return AppConfig(self.Data_Store, args.bucket, args.stdout, args.keep_data)
