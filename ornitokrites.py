#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:49:27 2013

@author: Lukasz Tracewski

Main module.

Identification of kiwi calls from audio recordings - main module.
"""

import sys
import matplotlib.pyplot as plt
import noise_reduction as nr
import recordings_io
import voice_enhancement as ve
import s3connection as s3
from segmentation import Segmentator

#
if (len(sys.argv) != 2):
    print "Incorrect syntax\nUsage: " + sys.argv[0] + " [kiwi bucket]"
    print "Example: " + sys.argv[0] + " kiwicalldata"
    sys.exit(1)

# Here all recordings will be stored
data_store = './Recordings/'

# Download recordings from a bucket
s3.read_data(bucket_name=sys.argv[1], output_recordings_dir=data_store)

# Generator; it will take recursively all .wav files from given directory
walker = recordings_io.Walker(data_store)

# For progress reporting
progress = 0.

# Segmentator divides a track into segments containing sound features (non-noise)
# and silence (noise)
segmentator = Segmentator()

# Read wave file on-the-fly (one at a time)
for rate, sample, sample_name in walker.read_wave(): 
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
    
    # Write cleared audio features to a file
    recordings_io.write(sample_name + '_seg.wav', rate, out_highpassed,
                        segments=segmented_sounds)
    
    # Plot spectrogram
    plt.specgram(out_highpassed, NFFT=2**11, Fs=rate)
    # and mark on it with vertical lines found audio features
    for start, end in segmented_sounds:
        start /= rate
        end /= rate
        plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2)
        plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
    plt.axis('tight')
    plt.savefig(sample_name + '.png')
    plt.clf()
    
    # Update progress
    progress += 1 
    print 'Processing %s %.1f%%' % (sample_name, 100.0 * progress / walker.count())   