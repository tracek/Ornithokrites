#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:49:27 2013

@author: Lukasz Tracewski

Main module.

Identification of kiwi calls from audio recordings - main module.
"""

import sys
import csv
import logging
import numpy as np
import nose.tools as nt
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import s3connection as s3
import noise_reduction as nr
import recordings_io
import voice_enhancement as ve
# import yaafelib as yf
from segmentation import Segmentator

logging.basicConfig(filename='/var/www/results/log.html', filemode='w', format='%(message)s <br/>', level=logging.INFO)
logging.info('<!DOCTYPE html>')

# Handle user input
# First argument is used as S3 bucket name
# If none specified then default is used - kiwicalldata
if (len(sys.argv) != 2):
    user_bucket = 'kiwicalldata'
    logging.info('No argument specified. Default bucket %s used.<br/><hr><br>', user_bucket)
else:
    user_bucket = sys.argv[1]

# Here all recordings will be stored
data_store = '/var/www/results/Recordings/'

# Download recordings from a bucket
s3.read_data(bucket_name=user_bucket, output_recordings_dir=data_store)

# Generator; it will take recursively all .wav files from given directory
walker = recordings_io.Walker(data_store)

# For progress reporting
progress = 0.

# Segmentator divides a track into segments containing sound features (non-noise)
# and silence (noise)
segmentator = Segmentator()

# Read wave file on-the-fly (one at a time)
for rate, sample, sample_name in walker.read_wave(): 
    logging.info('<h2>%s</h2>', sample_name.replace('/var/www/results/Recordings/',''))
    
    # Apply highpass filter to greatly reduce signal strength below 1500 Hz.  
    sample_highpassed = nr.highpass_filter(sample, rate, 1500)
    
    # Perform segmentation on high-passed sample
    segmentator.process(sample_highpassed, rate)
    
    # Perform spectral subtraction on sample (not high-passed!)
    try:
        noise = segmentator.get_next_silence(sample) # Get silence period
        out = ve.reduce_noise(sample, noise, 0) # Perform spectral subtraction
        noise = segmentator.get_next_silence(sample) # Try again
        out = ve.reduce_noise(out, noise, 0) # Perform spectral subtraction
    except KeyError, e: # Happens when there was not enough silence periods
        pass
    
    # Apply high-pass filter on spectral-subtracted sample
    out_highpassed = nr.highpass_filter(out, rate, 1200)
    
    # Get segments of signal that contain audio features
    segmented_sounds = segmentator.get_segmented_sounds()
    
    # Get features
#    fp = yf.FeaturePlan(sample_rate=rate)
#    success = fp.loadFeaturePlan('features.config')
#    nt.assert_true(success, 'features config not loaded correctly')
#    engine = yf.Engine()
#    engine.load(fp.getDataFlow())    
#    engine.reset()
#    
#    file_csv = open(sample_name + '.csv','wb')
#    header_written = False
#    sounds = []
#    for start, end in segmentator.get_segmented_sounds():
#        audio = out[start:end]
#        feats = engine.processAudio(np.array([audio]))
#        w = csv.DictWriter(file_csv, feats.keys())
#        if not header_written:    
#            w.writeheader()
#            header_written = True
#        w.writerow(feats)
#        sounds.append(feats)
#    file_csv.close()
    
    # Write cleared audio features to a file
    segmented_sample_name = sample_name + '_seg.wav'
    recordings_io.write(segmented_sample_name, rate, out_highpassed,
                        segments=segmented_sounds)
    logging.info('<audio controls><source src="%s" type="audio/wav"></audio>', 
                 segmented_sample_name.replace('/var/www/',''))
    
    # Plot spectrogram
    plt.specgram(out_highpassed, NFFT=2**11, Fs=rate)
    # and mark on it with vertical lines found audio features
    for start, end in segmented_sounds:
        start /= rate
        end /= rate
        plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2)
        plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
    plt.axis('tight')
    spectrogram_sample_name = sample_name + '.png'
    plt.savefig(spectrogram_sample_name)
    plt.clf()
    logging.info('<img src="%s" alt="Spectrogram">', spectrogram_sample_name.replace('/var/www/',''))
    
    # Update progress
    progress += 1 
    logging.info('Completed %s ', sample_name)
    logging.info('Progress: %.1f%%', 100.0 * progress / walker.count())
    logging.info('<hr>')