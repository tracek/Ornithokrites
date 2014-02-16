# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:49:27 2013

@author: Lukasz Tracewski

Test module
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import noise_reduction as nr
import recordings_io
import features

plt.ioff()
data_store = './Recordings/'
walker = recordings_io.Walker(data_store)
progress = 0.
#
#from sklearn import preprocessing
#from sklearn import svm
#import pickle

#file_model = open('model.pkl', 'rb')
#model = pickle.load(file_model)
#file_model.close()

for rate, sample, sample_name in walker.read_wave(): 
    
    noise_remover = nr.NoiseRemover()
    try:
        out = noise_remover.remove_noise(sample, rate)
    except ValueError:
        out = sample
        
    segmentator = noise_remover.segmentator
    segmented_sounds = segmentator.get_segmented_sounds()
    
    feature_extractor = features.FeatureExtractor()
    feature_extractor.process(out, rate, segmented_sounds)
    
#    X = feature_extractor.ExtractedFeatures
#    X = np.nan_to_num(X)
#    X = preprocessing.scale(X)
#    P = model.predict(X)
    
    feature_extractor.write_extracted_features_to_csv(sample_name + '_data')
    feature_extractor.plot_features(sample_name + '_features')
    
    plt.figure()
    plt.specgram(out, NFFT=2**11, Fs=rate)
    i = 0
    for start, end in segmented_sounds:
        start /= rate
        end /= rate
        plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2, ls='dashed')
        plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
        plt.text(start, 4000, i, fontsize=8)
        i += 1
        
    plt.savefig(sample_name + '_spec.png')
    plt.clf()    
    
    progress += 1 
    print 'Completed %s %.1f%%' % (sample_name, 100.0 * progress / walker.count())  