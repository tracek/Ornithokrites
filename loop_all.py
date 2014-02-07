# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:49:27 2013

@author: Lukasz Tracewski

Main module.

Identification of kiwi calls from audio recordings - main module.
"""

import matplotlib
matplotlib.use('Agg')
import numpy as np
import nose.tools as nt
import matplotlib.pyplot as plt
import noise_reduction as nr
import recordings_io
import voice_enhancement as ve
import yaafelib as yf
from segmentation import Segmentator
from wavelet_features import WaveletFeatures

plt.ioff()

# Here all recordings will be stored
data_store = './Recordings/female/'

# Download recordings from a bucket
#s3.read_data(output_recordings_dir=data_store)

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
    
    out = sample
    
    # Perform spectral subtraction on sample (not high-passed!)
    try:
        noise = segmentator.get_next_silence(sample) # Get silence period
        out = ve.reduce_noise(sample, noise, 0) # Perform spectral subtraction
        noise = segmentator.get_next_silence(sample) # Try again
        out = ve.reduce_noise(out, noise, 0) # Perform spectral subtraction
    except KeyError, e:
        print 'Recovery'
        seg2 = Segmentator(detector_type='energy', threshold=0.2)
        seg2.process(sample_highpassed, rate)
        segmented_sounds = seg2.get_segmented_sounds()
        try:
            noise = seg2.get_next_silence(sample)
            out = ve.reduce_noise(out, noise, 0)
            noise = seg2.get_next_silence(sample)
            out = ve.reduce_noise(out, noise, 0)
        except KeyError, e:    
            print 'Fail'
        
#    wf = WaveletFeatures()
#    out = wf.wavpack(out)
    
    # Apply high-pass filter on spectral-subtracted sample
    out = nr.highpass_filter(out, rate, 1200)
    
    # Get segments of signal that contain audio features
    segmented_sounds = segmentator.get_segmented_sounds()
    
    # Get features
    fp = yf.FeaturePlan(sample_rate=rate)
    success = fp.loadFeaturePlan('features_all.config')
    nt.assert_true(success, 'features config not loaded correctly')
    engine = yf.Engine()
    engine.load(fp.getDataFlow())    

    feats = engine.processAudio(np.array([out.astype('float64')]))

    plt.figure(figsize=(12,50))
    n = 16
    nx = 1
    
    ax = plt.subplot(n,nx,0)
    plt.specgram(out, NFFT=2**11, Fs=rate)
    for start, end in segmented_sounds:
        start /= rate
        end /= rate
        plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2)
        plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
    
    ax = plt.subplot(n,nx,1)
    plt.title('SpectralFlatness')
    plt.plot(feats['SpectralFlatness'])
    
    ax = plt.subplot(n,nx,2)
    plt.title('SpectralShapeStatistics - centroid')
    plt.plot(feats['SpectralShapeStatistics'][:,0])
    
    ax = plt.subplot(n,nx,3)
    plt.title('SpectralShapeStatistics - spread')
    plt.plot(feats['SpectralShapeStatistics'][:,1])
    
    ax = plt.subplot(n,nx,4)
    plt.title('PerceptualSpread')
    plt.plot(feats['PerceptualSpread'])
    
    ax = plt.subplot(n,nx,5)
    plt.title('SpectralSlope')
    plt.plot(feats['SpectralSlope'])
    
    ax = plt.subplot(n,nx,6)
    plt.title('PerceptualSharpness')
    plt.plot(feats['PerceptualSharpness'])
    
    ax = plt.subplot(n,nx,7)
    plt.title('SpectralDecrease')
    plt.plot(feats['SpectralDecrease'])
    
    ax = plt.subplot(n,nx,8)
    plt.title('ZCR')
    plt.plot(feats['ZCR'])
    
    ax = plt.subplot(n,nx,9)
    plt.title('OBSI - 0')
    plt.plot(feats['OBSI'][:,0])
    
    ax = plt.subplot(n,nx,10)
    plt.title('TemporalShapeStatistics - centroid')
    plt.plot(feats['TemporalShapeStatistics'][:,0])
    
    ax = plt.subplot(n,nx,11)
    plt.title('TemporalShapeStatistics - skewness')
    plt.plot(feats['TemporalShapeStatistics'][:,2])
    
    ax = plt.subplot(n,nx,12)
    plt.title('LPC - 0')
    plt.plot(feats['LPC'][:,0])
    
    ax = plt.subplot(n,nx,13)
    plt.title('LPC - 1')
    plt.plot(feats['LPC'][:,1])
    
    ax = plt.subplot(n,nx,14)
    plt.title('SpectralRolloff')
    plt.plot(feats['SpectralRolloff'])
    
    ax = plt.subplot(n,nx,15)
    plt.title('LSF - 7')
    plt.plot(feats['LSF'][:,7])
    
    plt.savefig(sample_name + '.png')
    plt.clf()

    # Write cleared audio features to a file
    recordings_io.write(sample_name + '_seg.wav', rate, out,
                        segments=segmented_sounds)
    
    # Update progress
    progress += 1 
    print 'Completed %s %.1f%%' % (sample_name, 100.0 * progress / walker.count())  
