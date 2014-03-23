# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 21:21:37 2014

@author: tracek
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
import scipy.io.wavfile as wav
import noise_reduction as nr
import scipy.signal as sig

path = './clicks/RFPT-BB6-20120127220002-0-60-KR4.wav'
#path = './clicks/RFPT-LPA-20111128233002-120-60-KR6.wav'
(rate, sample) = wav.read(path)
sample = sample.astype('float32')
#sample=np.tile(sample,2)

signal = nr.remove_clicks(sample, rate, 2**10, 1.2)
plt.plot(signal)