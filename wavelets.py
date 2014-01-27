# -*- coding: utf-8 -*-
"""
Created on Mon Dec 02 12:07:49 2013

@author: ltracews
"""
from __future__ import division

import scipy.io.wavfile as wav
import scipy.signal as sig
import numpy as np
import noise_reduction as nr
import pywt

def calculate_energy(data):
    return sum(data**2)
    
def normalize(data, feature_range=(-1, 1)):
    data_min = np.min(data, axis=0)
    data_range = np.max(data, axis=0) - data_min
    scale = (feature_range[1] - feature_range[0]) / data_range
    min_ = feature_range[0] - data_min * scale
    scaled_data = data * scale
    scaled_data += min_
    return scaled_data

path_recording = 'C:\\kiwi-calls\\female\\RFPT-LPA-20111211223002-720-60-KR6.wav'
(rate, sample) = wav.read(path_recording)

out = sample
# out = normalize(out)
out = nr.highpass_filter(out, rate, 1200)

out = out[291158:300249]
db10 = pywt.Wavelet('db10')
dec = pywt.wavedec(out, db10, level=6,mode='sym')

cA, cD = pywt.dwt(sample, db10)
results = []
results.append(sample)

elements_to_remove = 0
for i in np.arange(6):
    for k in np.arange(2**i):
        cA, cD = pywt.dwt(results[k], db10)
        results.append(cA)
        results.append(cD)
    elements_to_remove = 2**i
    results = results[elements_to_remove:]
    
bins = results[16:24] + results[48:56]
n = len(bins)
nc = len(results[0])    


bin_energies = []
avr_bin_energies = []

for i in np.arange(n):
    energy = calculate_energy(bins[i])
    bin_energies.append(energy)
    avr_bin_energies.append(energy / nc)
    
max_avr_energy = max(avr_bin_energies)
max_index = avr_bin_energies.index(max_avr_energy)

spread_bins = []
for i in np.arange(n):
    avr_energy = avr_bin_energies[i]
    Th1 = avr_energy / 6
    bin2 = bins[i]**2
    bin2_Th1 = bin2[bin2 > Th1]
    spread = sum(bin2_Th1)
    spread_bins.append(spread / len(bin2_Th1))
    
spread = sum(spread_bins) / len(spread_bins)
