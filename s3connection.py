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
import Tkinter
import tkFileDialog


class RecordingsFetcher(object):
    """ Class for getting WAVE recordings from a given S3 bucket """
    def __init__(self):
        self._log = logging.getLogger('log.html')

    def get_next_recording(self, bucket_name, data_store):
        """
        Generator for getting WAVE files. The data will be provided on-demand basis.

        Parameters
        -------------
        bucket_name : string
            Name of AWS S3 bucket. If none provided then it is assumed data is available locally.
        data_store : string
            In case bucket name is provided, this location will be used for storing the data.
            Once a recording is there, or no bucket was provided, from this place data will be
            read recursively. In none provided, then user has to select a single file through
            a file dialog.

        Returns
        ------------
        samplerate : int
            Rate of the sample in Hz
        sample : 1-d array
            Wave file read as numpy array of int16
        name : string
            Name of a wave file
        """
        if bucket_name:  # Download data from a bucket
            self._connect_to_bucket(bucket_name)
            for key in self.Bucket.list():
                if key.name.endswith('.wav') and not key.name.startswith('5mincounts'):
                    # self._log.info('Downloading %s', key.name)
                    path = os.path.join(data_store, key.name)
                    _make_sure_dir_exists(path)
                    key.get_contents_to_filename(path)  # Download the file
                    (rate, sample) = wav.read(path)
                    yield rate, sample, path
        elif data_store:  # Get locally stored data
            for dirpath, dirnames, filenames in os.walk(data_store):
                for filename in [f for f in filenames if f.endswith('.wav')]:
                    path = os.path.join(dirpath, filename)
                    (rate, sample) = wav.read(path)
                    yield rate, sample, path
        else:  # Interactive mode - let user select a signle file
            root = Tkinter.Tk()
            root.withdraw()
            filename = tkFileDialog.askopenfilename()
            (rate, sample) = wav.read(path)
            yield rate, sample, path

    def get_recordings(self, app_config, inq):
        """
        Get data from selected location and pass it to the queue.

        Parameters
        -------------
        bucket_name : string
            Name of AWS S3 bucket. If none provided then it is assumed data is available locally.
        data_store : string
            In case bucket name is provided, this location will be used for storing the data.
            Once a recording is there, or no bucket was provided, from this place data will be
            read recursively. In none provided, then user has to select a single file through
            a file dialog.
        inq : multiprocessing.Queue
            The recordings shall be put on the queue.

        Returns
        ------------
        samplerate : int
            Rate of the sample in Hz.
        sample : 1-d array
            Wave file read as numpy array of int16.
        name : string
            Name of a wave file.
        """
        if app_config.bucket:  # Download data from a bucket
            self._connect_to_bucket(app_config.bucket)
            for key in self.Bucket.list():
                if key.name.endswith('.wav') and not key.name.startswith('5mincounts'):
                    # self._log.info('Downloading %s', key.name)
                    path = os.path.join(app_config.data_store, key.name)
                    _make_sure_dir_exists(path)
                    key.get_contents_to_filename(path)  # Download the file
                    (rate, sample) = wav.read(path)
                    inq.put((rate, sample, path))
        elif app_config.data_store:  # Get locally stored data
            for dirpath, dirnames, filenames in os.walk(app_config.data_store):
                for filename in [f for f in filenames if f.endswith('.wav')]:
                    path = os.path.join(dirpath, filename)
                    (rate, sample) = wav.read(path)
                    inq.put((rate, sample.astype('float32'), path))
        else:  # Interactive mode - parallel processing on one file makes no sense ...
            root = Tkinter.Tk()
            root.withdraw()
            filename = tkFileDialog.askopenfilename()
            (rate, sample) = wav.read(path)
            inq.put((rate, sample, path))

        for i in range(app_config.no_processes):
            inq.put("STOP")

    def _connect_to_bucket(self, bucket_name):
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


def _make_sure_dir_exists(filename):
    # Create recursively directory if it does not exist.
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
