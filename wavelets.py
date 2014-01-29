# -*- coding: utf-8 -*-
"""
Created on Mon Dec 02 12:07:49 2013

@author: ltracews
"""

from collections import namedtuple
import numpy as np
import pywt

Features = namedtuple('Features', 'max_avr_energy position spread')

class WaveletFeatures(object):
    
    def __init__(self, wavelet_name='db10'):
        self._wavelet = pywt.Wavelet(wavelet_name)
        
    def decompose(self, data, level=6, mode='sym'):
        results = []
        results.append(data)
        elements_to_remove = 0
        for i in np.arange(level):
            for k in np.arange(2**i):
                cA, cD = pywt.dwt(results[k], self._wavelet)
                results.append(cA)
                results.append(cD)
            elements_to_remove = 2**i
            results = results[elements_to_remove:]
        results = results[20:24] + results[52:56]
        results_array = np.array(results)
        del results
        return results_array
        
    def calculate_energy(self, data):
        return (data**2).sum()
        
    def calculate_features(self, wavelet_coeffs):
        n = len(wavelet_coeffs)
        nc = len(wavelet_coeffs[0])
        
        bin_energies = []
        avr_bin_energies = []
        
        for i in np.arange(n):
            energy = self.calculate_energy(wavelet_coeffs[i])
            bin_energies.append(energy)
            avr_bin_energies.append(energy / nc)
            
        max_avr_energy = max(avr_bin_energies)

        position = avr_bin_energies.index(max_avr_energy)
        
        spread_bins = []
        
        for i in np.arange(n):
            bins2 = wavelet_coeffs[i]**2
            Th1 = avr_bin_energies[i] / 6
            bins2_above_Th1 = bins2[bins2 > Th1]
            spread = bins2_above_Th1.sum() / len(bins2_above_Th1)
            spread_bins.append(spread)
            
        spread = sum(spread_bins) / len(spread_bins)
        
        return Features(max_avr_energy, position, spread) 
        
    def get_features(self, data):
        wavelet_coefficients = self.decompose(data)
        return self.calculate_features(wavelet_coefficients), wavelet_coefficients
        
    def wavpack(self, data):
        packet = pywt.WaveletPacket(data, self._wavelet)
        sixth = packet.get_level(6)
        
        cutoff = 41
        for i in np.arange(cutoff):
            sixth[i].data = np.zeros(len(sixth[i].data))
        for i in np.arange(cutoff, len(sixth)):
            sixth[i].data = pywt.thresholding.soft(sixth[i].data, np.std(sixth[i].data))
        
        reconstructed = packet.reconstruct()
        return reconstructed


if __name__ == '__main__':
    import recordings_io
    import matplotlib.pyplot as plt
    import noise_reduction as nr
    import segmentation 
    import voice_enhancement as ve    
    import Tkinter, tkFileDialog
    root = Tkinter.Tk()
    root.withdraw()
    path_recordings = tkFileDialog.askopenfilename()
    # path_recordings = '/home/tracek/Ptaszki/Recordings/female/RFPT-LPA-20111126214502-240-60-KR6.wav'
    (rate, sample) = recordings_io.read(path_recordings)
    sample = sample.astype('float32')
    sample_highpassed = nr.highpass_filter(sample, rate, 1500)
    segmentator = segmentation.Segmentator()
    segmentator.process(sample_highpassed, rate)
    
    silence = segmentator.get_silence()
    segmented_sounds = segmentator.get_segmented_sounds()
    
    out = sample

    try:
        noise = segmentator.get_next_silence(sample)
        out = ve.reduce_noise(sample, noise, 0)
        noise = segmentator.get_next_silence(sample)
        out = ve.reduce_noise(out, noise, 0)
    except KeyError, e:
        print e
#    
    out = nr.highpass_filter(out, rate, 1200) 
    
#    recordings_io.write('out' + '_seg.wav', rate, out, segments=segmented_sounds)
#    
    wave_feat = WaveletFeatures()
#    features = []
#    coeffs = []
#
#    for start, end in segmentator.get_segmented_sounds():
#        audio = out[start:end]
#        feature_segment, coeff = wave_feat.get_features(audio)
#        features.append(feature_segment)
#        coeffs.append(coeff)
#        
#    co = np.array(coeffs)
#    del coeffs
    
    out2 = wave_feat.wavpack(out)
    
    plt.subplot(311)    
    plt.specgram(out, NFFT=2**11, Fs=rate)
    # and mark on it with vertical lines found audio features
    for start, end in segmented_sounds:
        start /= rate
        end /= rate
        plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2)
        plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
    plt.axis('tight')    
    plt.subplot(312)
    plt.plot(out2)
    plt.subplot(313)
    plt.plot(out)
    plt.show()
