#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 19:03:15 2014

@author: tracek
"""

import os
import logging
import Tkinter, tkFileDialog
from argparse import ArgumentParser
import s3connection
import recordings_io

parser = ArgumentParser(description='Automatic identification of kiwi calls from audio recordings',
                        prog='Ornithokrites', epilog='lukasz.tracewski@gmail.com')
parser.add_argument('-b', '--bucket', help='Amazon Web Services S3 bucket name')
parser.add_argument('-d', '--datastore', help='Directory to process')
args = parser.parse_args()

if args.bucket:
    if args.datastore:
        data_store = args.datastore
    else:
        data_store = '/var/www/results/Recordings/'
    logging_file = os.path.join(data_store, 'log.html')
    s3connection.read_data(bucket_name=args.bucket, output_recordings_dir=data_store)
elif args.datastore:
    logging_file = './log.html'
    data_store = args.datastore
else:
    logging_file = './log.html'
    root = Tkinter.Tk()
    root.withdraw()
    data_store = tkFileDialog.askopenfilename()
    
logging.basicConfig(filename=logging_file, filemode='w', format='%(message)s <br/>', level=logging.INFO)
logging.info('<!DOCTYPE html>')

walker = recordings_io.Walker(data_store)