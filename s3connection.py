# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 12:58:13 2014

@author: tracek
"""

import os
import sys
import boto

def read_data(bucket_name='kiwicalldata'):
    try:
        print 'Connecting to S3 ...'
        s3 = boto.connect_s3()
    except:
        print 'Failure while connecting to S3. Check credentials.'
        sys.exit(1)
    try:
        print 'Connection established. Fetching bucket ...'
        bucket = s3.get_bucket(bucket_name)
    except:
        print 'Failure while connecting to bucket. Check if bucket exists.'
        sys.exit(1)    
    
    print 'Bucket ready. Getting data ...'
    for key in bucket.list():
        if key.name.endswith( '.wav' ) and not key.name.startswith('5mincounts'):
            print 'Downloading ' + key.name
            _make_sure_dir_exists(key.name)
            key.get_contents_to_filename(key.name)
            
def _make_sure_dir_exists(filename):
    dir_name = os.path.dirname(filename)
    if not os.path.exists( dir_name ):
        os.makedirs( dir_name )


if __name__ == '__main__':
    read_data()