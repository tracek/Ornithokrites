# -*- coding: utf-8 -*-
"""
Created on Mon Dec 02 12:07:49 2013

@author: ltracews
"""

import sys
import itertools
import numpy as np
import matplotlib.pyplot as plt
import yaafelib
import wavelets

class FeatureExtractor(object):
    
    def __init__(self, frame_overlap=512, wavelet_type='sym10'):
        self._frame_overlap = frame_overlap
        self._wavelet_type = wavelet_type

    def process(self, signal, rate, segments, wavelet_decomposition_level=6):
        """ Extract features """
        
        self.ExtractedFeaturesList = ['LPC0_mm', 'LPC1_mean', 'LPC1_max', 'LPC1_mm', \
            'LSF7_min', 'LSF7_mean', 'LSF7_mm', 'SpectralFlatness_min', 'SpectralFlatness_mean', \
            'SSS_centroid_min', 'SSS_centroid_mean', 'SSS_centroid_mm', 'SSS_spread_min', \
            'SSS_spread_mean', 'SSS_spread_mm', 'PerceptualSpread_min', 'PerceptualSpread_mean', \
            'PerceptualSpread_mm', 'SpectralSlope_min', 'SpectralSlope_mean', 'SpectralSlope_mm', \
            'PerceptualSharpness_min', 'PerceptualSharpness_mean', 'PerceptualSharpness_mm', \
            'SpectralDecrease_max', 'SpectralDecrease_mean', 'SpectralDecrease_mm', \
            'OBSI0_max', 'OBSI0_mm', 'SpectralRolloff_min', 'SpectralRolloff_mean', \
            'wavelets_max_avr_energy', 'wavelets_max_position', 'wavelets_spread']
        
        self._signal = signal
        self._rate = rate
        self._segments = segments

        """ Calculate spectral and temporal features """
        feature_plan = yaafelib.FeaturePlan(sample_rate=rate)
        success = feature_plan.loadFeaturePlan('features_all.config')
        if not success:
            sys.exit('Feature plan not loaded correctly')

        engine = yaafelib.Engine()
        engine.load(feature_plan.getDataFlow())    
        self.Features = engine.processAudio(np.array([signal.astype('float64')]))
        
        """ Initialize wavelet features
            Based on "Wavelets in Recognition of Bird Sounds" by A. Selin et al.
            EURASIP Journal on Advances in Signal Processing 2007, 2007:051806 """
        wavelets_calculator = wavelets.Wavelets(self._wavelet_type)
        wavelet_coefficients = wavelets_calculator.decompose(signal, wavelet_decomposition_level)
        
        no_segments = len(segments)
                
        self.ExtractedFeatures = np.zeros(shape=(no_segments, len(self.ExtractedFeaturesList)))          
        
        LPC0 = self.Features['LPC'][:,0]
        LPC1 = self.Features['LPC'][:,1]
        LSF7 = self.Features['LSF'][:,7]
        SpectralFlatness = self.Features['SpectralFlatness']
        SSS_centroid = self.Features['SpectralShapeStatistics'][:,0]
        SSS_spread = self.Features['SpectralShapeStatistics'][:,1]
        PerceptualSpread = self.Features['PerceptualSpread']
        SpectralSlope = self.Features['SpectralSlope']
        PerceptualSharpness = self.Features['PerceptualSharpness']
        SpectralDecrease = self.Features['SpectralDecrease']
        OBSI0 = self.Features['OBSI'][:,0]
        SpectralRolloff = self.Features['SpectralRolloff']
        
        for i, segment in enumerate(segments):
            start = segment[0] / self._frame_overlap - 1
            end = segment[1] / self._frame_overlap + 1
            
            """ Wavelets """
            start_wavelet = segment[0] / 2**wavelet_decomposition_level - 10
            end_wavelet = segment[1] / 2**wavelet_decomposition_level + 10
            wavelets_max_avr_energy, wavelets_max_position, wavelets_spread = \
                wavelets_calculator.calculate_features(wavelet_coefficients, start_wavelet, end_wavelet)
            
            self.ExtractedFeatures[i,0] = maxmin(LPC0[start:end])
            self.ExtractedFeatures[i,1] = LPC1[start:end].max()   
            self.ExtractedFeatures[i,2] = LPC1[start:end].mean()
            self.ExtractedFeatures[i,3] = maxmin(LPC1[start:end])
            self.ExtractedFeatures[i,4] = LSF7[start:end].min()
            self.ExtractedFeatures[i,5] = LSF7[start:end].mean()
            self.ExtractedFeatures[i,6] = maxmin(LSF7[start:end])
            self.ExtractedFeatures[i,7] = SpectralFlatness[start:end].min()
            self.ExtractedFeatures[i,8] = SpectralFlatness[start:end].mean()
            self.ExtractedFeatures[i,9] = SSS_centroid[start:end].min()      
            self.ExtractedFeatures[i,10] = SSS_centroid[start:end].mean()
            self.ExtractedFeatures[i,11] = maxmin(SSS_centroid[start:end])
            self.ExtractedFeatures[i,12] = SSS_spread[start:end].min() 
            self.ExtractedFeatures[i,13] = SSS_spread[start:end].mean()
            self.ExtractedFeatures[i,14] = maxmin(SSS_spread[start:end])
            self.ExtractedFeatures[i,15] = PerceptualSpread[start:end].min()  
            self.ExtractedFeatures[i,16] = PerceptualSpread[start:end].mean()
            self.ExtractedFeatures[i,17] = maxmin(PerceptualSpread[start:end])
            self.ExtractedFeatures[i,18] = SpectralSlope[start:end].min()   
            self.ExtractedFeatures[i,19] = SpectralSlope[start:end].mean()
            self.ExtractedFeatures[i,20] = maxmin(SpectralSlope[start:end])   
            self.ExtractedFeatures[i,21] = PerceptualSharpness[start:end].min() 
            self.ExtractedFeatures[i,22] = PerceptualSharpness[start:end].mean()
            self.ExtractedFeatures[i,23] = maxmin(PerceptualSharpness[start:end])  
            self.ExtractedFeatures[i,24] = SpectralDecrease[start:end].max()  
            self.ExtractedFeatures[i,25] = SpectralDecrease[start:end].mean()
            self.ExtractedFeatures[i,26] = maxmin(SpectralDecrease[start:end]) 
            self.ExtractedFeatures[i,27] = OBSI0[start:end].max()
            self.ExtractedFeatures[i,28] = maxmin(OBSI0[start:end])
            self.ExtractedFeatures[i,29] = SpectralRolloff[start:end].min()        
            self.ExtractedFeatures[i,30] = SpectralRolloff[start:end].mean()  
            self.ExtractedFeatures[i,31] = wavelets_max_avr_energy
            self.ExtractedFeatures[i,32] = wavelets_max_position
            self.ExtractedFeatures[i,33] = wavelets_spread

        
    def plot_features(self, file_name=''):
        plt.figure(figsize=(12,50))
        n = 14
        nx = 1
        
        plt.subplot(n,nx,0)
        plt.specgram(self._signal, NFFT=2**11, Fs=self._rate)
        for start, end in self._segments:
            start /= self._rate
            end /= self._rate
            plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2)
            plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
        
        plt.subplot(n,nx,1)
        plt.title('SpectralFlatness')
        plt.plot(self.Features['SpectralFlatness'])
        
        plt.subplot(n,nx,2)
        plt.title('SpectralShapeStatistics - centroid')
        plt.plot(self.Features['SpectralShapeStatistics'][:,0])
        
        plt.subplot(n,nx,3)
        plt.title('SpectralShapeStatistics - spread')
        plt.plot(self.Features['SpectralShapeStatistics'][:,1])
        
        plt.subplot(n,nx,4)
        plt.title('PerceptualSpread')
        plt.plot(self.Features['PerceptualSpread'])
        
        plt.subplot(n,nx,5)
        plt.title('SpectralSlope')
        plt.plot(self.Features['SpectralSlope'])
        
        plt.subplot(n,nx,6)
        plt.title('PerceptualSharpness')
        plt.plot(self.Features['PerceptualSharpness'])
        
        plt.subplot(n,nx,7)
        plt.title('SpectralDecrease')
        plt.plot(self.Features['SpectralDecrease'])
        
        plt.subplot(n,nx,8)
        plt.title('ZCR')
        plt.plot(self.Features['ZCR'])
        
        plt.subplot(n,nx,9)
        plt.title('OBSI - 0')
        plt.plot(self.Features['OBSI'][:,0])
        
        plt.subplot(n,nx,10)
        plt.title('LPC - 0')
        plt.plot(self.Features['LPC'][:,0])
        
        plt.subplot(n,nx,11)
        plt.title('LPC - 1')
        plt.plot(self.Features['LPC'][:,1])
        
        plt.subplot(n,nx,12)
        plt.title('SpectralRolloff')
        plt.plot(self.Features['SpectralRolloff'])
        
        plt.subplot(n,nx,13)
        plt.title('LSF - 7')
        plt.plot(self.Features['LSF'][:,7])
        
        if file_name:
            plt.savefig(file_name + '.png')
            plt.clf()
        else:
            plt.show()
        
    def plot_extracted_features(self, file_name=''):
        plt.figure(figsize=(30,60))
        no_features = np.shape(self.ExtractedFeatures)[1]
        for column in np.arange(no_features):
            ax = plt.subplot(7,5,column+1)
            plt.plot(self.ExtractedFeatures[:,column])
            plt.title(self.ExtractedFeaturesList[column])
            ax.set_xticks([])
        if file_name:
            plt.savefig(file_name + '.png')
            plt.clf()
        else:
            plt.show()
        
    def write_extracted_features_to_csv(self, file_name):
        csv_header = ','.join(itertools.chain(self.ExtractedFeaturesList)) + '\n'
        np.savetxt(file_name + '.csv', self.ExtractedFeatures, delimiter=',', header=csv_header)
        
        
def maxmin(array):
    max_val = array.max()
    min_val = array.min()
    return max_val - min_val
    
