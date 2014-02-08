# -*- coding: utf-8 -*-
"""
Created on Mon Dec 02 12:07:49 2013

@author: ltracews
"""

from collections import namedtuple
import numpy as np
import pywt

# WaveletFeatures = namedtuple('WaveletFeatures', 'max_avr_energy position spread')

class Wavelets(object):
    
    def __init__(self, wavelet_name='sym10'):
        self._wavelet = pywt.Wavelet(wavelet_name)
        
#    def decompose(self, data, level=6, mode='sym'):
#        results = []
#        results.append(data)
#        elements_to_remove = 0
#        for i in np.arange(level):
#            for k in np.arange(2**i):
#                cA, cD = pywt.dwt(results[k], self._wavelet)
#                results.append(cA)
#                results.append(cD)
#            elements_to_remove = 2**i
#            results = results[elements_to_remove:]
#        results = results[20:24] + results[52:56]
#        results_array = np.array(results)
#        del results
#        return results_array
        
    def decompose(self, data, level=6):
        packet = pywt.WaveletPacket(data, self._wavelet)
        q = packet.get_level(level)
        decomposed = []
        for i in np.arange(16, 32):
            decomposed.append(q[i].data)
        for i in np.arange(46, 64):
            decomposed.append(q[i].data)
        decomposed_array = np.array(decomposed)
        return decomposed_array
        
    def calculate_energy(self, data):
        return (data**2).sum()
        
    def calculate_features(self, wavelet_coeffs, start, end):
        
        n = len(wavelet_coeffs)
        nc = len(wavelet_coeffs[0][start:end])
        
        bin_energies = []
        avr_bin_energies = []
        
        for i in np.arange(n):
            energy = self.calculate_energy(wavelet_coeffs[i][start:end])
            bin_energies.append(energy)
            avr_bin_energies.append(energy / nc)
            
        max_avr_energy = max(avr_bin_energies)

        position = avr_bin_energies.index(max_avr_energy)
        
        spread_bins = []
        
        for i in np.arange(n):
            bins2 = wavelet_coeffs[i][start:end]**2
            Th1 = avr_bin_energies[i] / 6
            bins2_above_Th1 = bins2[bins2 > Th1]
            spread = bins2_above_Th1.sum() / len(bins2_above_Th1)
            spread_bins.append(spread)
            
        spread = sum(spread_bins) / len(spread_bins)
        
        return max_avr_energy, position, spread
        
    def get_features(self, data):
        wavelet_coefficients = self.decompose_wavpack(data)
        return self.calculate_features(wavelet_coefficients), wavelet_coefficients
        
    def wavpack(self, data):
        packet = pywt.WaveletPacket(data, self._wavelet)
        q = packet.get_level(6)
        
        l = len(q[0].data)
        for i in np.arange(0, 16):
            q[i].data = np.zeros(l)
        for i in np.arange(16, 32):
            q[i].data = pywt.thresholding.soft(q[i].data, np.std(q[i].data))
        for i in np.arange(32, 47):
            q[i].data = np.zeros(l)
        for i in np.arange(47, 64):
            q[i].data = pywt.thresholding.soft(q[i].data, np.std(q[i].data))   
        
        reconstructed = packet.reconstruct()
        return reconstructed
        
    def cut_sharp(self, data):
        packet = pywt.WaveletPacket(data, self._wavelet)
        q = packet.get_level(6)
        l = len(q[0].data)
        for i in np.arange(0, 16):
            q[i].data = np.zeros(l)
        for i in np.arange(16, 20):
            q[i].data = pywt.thresholding.soft(q[i].data, 1.5 * np.std(q[i].data))
        for i in np.arange(20, 48):
            q[i].data = np.zeros(l)
        for i in np.arange(48, 52):
            q[i].data = pywt.thresholding.soft(q[i].data, 1.5 * np.std(q[i].data))
        for i in np.arange(52, 64):
            q[i].data = np.zeros(l) 
        reconstructed = packet.reconstruct()
        return reconstructed           


if __name__ == '__main__':
    import recordings_io
    import matplotlib.pyplot as plt
    import noise_reduction as nr
    import Tkinter, tkFileDialog
    
    root = Tkinter.Tk()
    root.withdraw()
    path_recordings = tkFileDialog.askopenfilename()
    # path_recordings = '/home/tracek/Ptaszki/Recordings/female/RFPT-LPA-20111126214502-240-60-KR6.wav'
    (rate, sample) = recordings_io.read(path_recordings)
    sample = sample.astype('float32')
    
    noise_remover = nr.NoiseRemover(sample, rate)
    try:
        out = noise_remover.remove_noise()
    except ValueError:
        out = sample
        
    segmentator = noise_remover.segmentator
    segmented_sounds = segmentator.get_segmented_sounds()
    
    wave = WaveletFeatures()
    wave_feat, coeffs = wave.get_features(out)
           
    plt.specgram(out, NFFT=2**11, Fs=rate)
    # and mark on it with vertical lines found audio features
    for start, end in segmented_sounds:
        start /= rate
        end /= rate
        plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2, ls='dashed')
        plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
    plt.axis('tight')    
    plt.show()
