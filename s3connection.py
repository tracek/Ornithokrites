# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 12:58:13 2014

@author: Lukasz Tracewski

Module for getting data from given S3 bucket.
"""

import os
import sys
import logging
import boto
import scipy.io.wavfile as wav

class RecordingsFetcher(object):
    """ Class for getting WAVE recordings from a given S3 bucket """
    def __init__(self, data_store='./Recordings/'):
        self._output_recordings_dir = data_store
        self._log = logging.getLogger('log.html')
            
    def connect_to_bucket(self, bucket_name='kiwicalldata'):
        try:
            self._log.info('Connecting to S3 ...')
            s3 = boto.connect_s3()
        except:
            self._log.critical('Failure while connecting to S3. Check credentials.')
            sys.exit(1)
        try:
            self._log.info('Connection established. Fetching bucket %s...', bucket_name)
            self.Bucket = s3.get_bucket(bucket_name)
        except:
            self._log.critical('Failure while connecting to bucket. Check if bucket exists.')
            sys.exit(1)
            
        self._log.info('Bucket ready.')
        
        return self.Bucket
        
    def get_next_recording(self):
        for key in self.Bucket.list():
            if key.name.endswith('.wav') and not key.name.startswith('5mincounts'):
                self._log.info('Downloading %s', key.name)
                path = os.path.join(self._output_recordings_dir, key.name)
                _make_sure_dir_exists(path)
                key.get_contents_to_filename(path)
                (rate, sample) = wav.read(path)
                yield rate, sample, path     
        

def read_data(bucket_name='kiwicalldata', output_recordings_dir='./Recordings/'):
    """ 
    Downloads data from bucket to the specified directory.
    
    Parameters
    ----------
    bucket_name : string (default = 'kiwicalldata')
        Name of a S3 bucket to connect.
    output_recordings_dir : string (default = './Recordings/')
        Output directory where downloaded data will be stored. If directory
        does not exist it will be created recursively.
        
    Returns
    -------
    Nothing
    """
    log = logging.getLogger('log.html') 
    devlog = logging.getLogger('devlog.html') 
        
    try:
        log.info('Connecting to S3 ...')
        s3 = boto.connect_s3()
    except:
        logging.critical('Failure while connecting to S3. Check credentials.')
        sys.exit(1)
    try:
        log.info('Connection established. Fetching bucket %s...', bucket_name)
        bucket = s3.get_bucket(bucket_name)
    except:
        log.critical('Failure while connecting to bucket. Check if bucket exists.')
        sys.exit(1)    
    
    log.info('Bucket ready. Getting data ...')
    for key in bucket.list():
        if key.name.endswith('.wav') and not key.name.startswith('5mincounts'):
            devlog.info('Downloading %s', key.name)
            path = os.path.join(output_recordings_dir, key.name)
            _make_sure_dir_exists(path)
            key.get_contents_to_filename(path)
            
def _make_sure_dir_exists(filename):
    # Create recursively directory if it does not exist.
    dir_name = os.path.dirname(filename)
    if not os.path.exists( dir_name ):
        os.makedirs( dir_name )

""" Test """
if __name__ == '__main__':
    fetcher = RecordingsFetcher('TestRecordings')
    fetcher.connect_to_bucket()
    
    log = logging.getLogger('log.html') 
    log.addHandler(logging.StreamHandler())
    
    for rate, sample, path in fetcher.get_next_recording():
        print path, ' ', rate
        
    
    
    
    
    
    
    
    
    
    