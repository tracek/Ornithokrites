# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 12:32:13 2014

@author: Lukasz Tracewski
"""

import recordings_io
import matplotlib.pyplot as plt
import noise_reduction as nr
import features

import Tkinter, tkFileDialog
root = Tkinter.Tk()
root.withdraw()
path_recordings = tkFileDialog.askopenfilename()

#path_recordings = '/home/tracek/Ptaszki/Recordings/male/RFPT-LPA-20111128233002-120-60-KR6.wav'
#path_recordings = '/home/tracek/Ptaszki/Recordings/male/RFPT-LPA-20111210220002-120-60-KR6.wav'
#path_recordings = '/home/tracek/Ptaszki/RFPT-LPA-20111128233002-120-60-KR6.wav'

(rate, sample) = recordings_io.read(path_recordings)
sample = sample.astype('float32')

noise_remover = nr.NoiseRemover()
try:
    out = noise_remover.remove_noise(sample, rate)
except ValueError:
    out = sample
    
segmentator = noise_remover.segmentator
segmented_sounds = segmentator.get_segmented_sounds()

feature_extractor = features.FeatureExtractor()
feature_extractor.process(out, rate, segmented_sounds)

recordings_io.write('out' + '_seg.wav', rate, out, segments=segmented_sounds)

plt.specgram(out, NFFT=2**11, Fs=rate)
for start, end in segmented_sounds:
    start /= rate
    end /= rate
    plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2, ls='dashed')
    plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
plt.axis('tight')

#plt.subplot(212)
plt.show()
