# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 15:59:17 2013

@author: tracek
"""

import warnings
import pdb
import numpy as np

def err_handler(type, flag):
    print "Floating point error (%s), with flag %s" % (type, flag)
    pdb.set_trace() 

warnings.simplefilter('error',Warning)
np.seterr('log')
saved_handler = np.seterrcall(err_handler)
save_err = np.seterr(all='call')

m = aubio.mfcc(win_s, n_filters, n_coeffs, rate)
p = aubio.pvoc(win_s, hop_s)
mfccs = np.zeros([n_coeffs,])
for start, end in segmentator.get_segmented_sounds():
    sound = out[start:end].astype('float32')
    mfcc_win = np.zeros(n_coeffs)
    for i in np.arange(0, len(sound), win_s):
        spec = p(sound)
        mfcc_out = m(spec)
        mfcc_win += mfcc_out
    mfcc_win /= np.ceil(len(sound) * 1.0 / win_s)
    mfccs = np.vstack((mfcc_win, mfcc_out))    
    
m = aubio.mfcc(win_s, n_filters, n_coeffs, rate)
p = aubio.pvoc(win_s, hop_s)
mfccs = np.zeros([n_coeffs,])
for start, end in segmentator.get_segmented_sounds():
    sound = out[start:end].astype('float32')
    mfcc_win = np.zeros(n_coeffs)
    inter = np.arange(0, len(sound), win_s)
    for i, j in zip(inter, inter[1:]):
        spec = p(sound[i:j])
        mfcc_out = m(spec)
        mfcc_win += mfcc_out
    mfcc_win /= np.ceil(len(sound) * 1.0 / win_s)
    mfccs = np.vstack((mfccs, mfcc_win))    

features_list = ['AutoCorrelation', 'LPC', 'LSF', 'MelSpectrum', 'OBSIR', 'PerceptualSharpness',
                 'PerceptualSpread', 'SpectralCrestFactorPerBand', 'SpectralDecrease', 
                 'SpectralFlatness', 'SpectralFlatnessPerBand', 'SpectralFlux', 'SpectralRolloff',
                 'SpectralShapeStatistics', 'SpectralSlope', 'SpectralVariation',
                 'TemporalShapeStatistics', 'ZCR']
features_keys = [s + ': ' for s in features_list]
features = dict(zip(features_keys, features_list))    
    
for key, value in features.iteritems():
    success = fp.addFeature(key + value)
    if not success:
        print 'Adding of feature ' + value + ' has failed'
        break
    else:
        print key + value