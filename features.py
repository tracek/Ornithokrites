# -*- coding: utf-8 -*-
"""
Created on Mon Dec 02 12:07:49 2013

@author: ltracews
"""

import sys
import csv
from collections import OrderedDict
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
    
        LPC0_mm = np.zeros(no_segments)
        LPC1_mean = np.zeros(no_segments)
        LPC1_max = np.zeros(no_segments)
        LPC1_mm = np.zeros(no_segments)
        LSF7_min = np.zeros(no_segments)
        LSF7_mean = np.zeros(no_segments)
        LSF7_mm = np.zeros(no_segments)
        SpectralFlatness_min = np.zeros(no_segments)
        SpectralFlatness_mean = np.zeros(no_segments)
    #    SpectralFlatness_mm = np.zeros(no_segments)
        SSS_centroid_min = np.zeros(no_segments)
        SSS_centroid_mean = np.zeros(no_segments)
        SSS_centroid_mm = np.zeros(no_segments)
        SSS_spread_min = np.zeros(no_segments)
        SSS_spread_mean = np.zeros(no_segments)
        SSS_spread_mm = np.zeros(no_segments)
        PerceptualSpread_min = np.zeros(no_segments)
        PerceptualSpread_mean = np.zeros(no_segments)
        PerceptualSpread_mm = np.zeros(no_segments)
        SpectralSlope_min = np.zeros(no_segments)
        SpectralSlope_mean = np.zeros(no_segments)
        SpectralSlope_mm = np.zeros(no_segments)  
        PerceptualSharpness_min = np.zeros(no_segments)
        PerceptualSharpness_mean = np.zeros(no_segments)
        PerceptualSharpness_mm = np.zeros(no_segments)
        SpectralDecrease_max = np.zeros(no_segments)
        SpectralDecrease_mean = np.zeros(no_segments)
        SpectralDecrease_mm = np.zeros(no_segments)
    #    ZCR_mm = np.zeros(no_segments)
        OBSI0_max = np.zeros(no_segments)
        OBSI0_mm = np.zeros(no_segments)
        SpectralRolloff_min = np.zeros(no_segments)
        SpectralRolloff_mean = np.zeros(no_segments)
    #    MFCC2_mm = np.zeros(no_segments)
    #    MFCC3_mm = np.zeros(no_segments)
    #    MFCC4_mm = np.zeros(no_segments)
    #    MFCC5_mm = np.zeros(no_segments)
    #    MFCC6_mm = np.zeros(no_segments)
        wavelets_max_avr_energy = np.zeros(no_segments)
        wavelets_max_position = np.zeros(no_segments)
        wavelets_spread = np.zeros(no_segments)
        
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
    #    ZCR = self.Features['ZCR']
        OBSI0 = self.Features['OBSI'][:,0]
        SpectralRolloff = self.Features['SpectralRolloff']
    #    MFCC2 = self.Features['MFCC'][:,2]
    #    MFCC3 = self.Features['MFCC'][:,3]
    #    MFCC4 = self.Features['MFCC'][:,4]
    #    MFCC5 = self.Features['MFCC'][:,5]
    #    MFCC6 = self.Features['MFCC'][:,6]
        
        for i, segment in enumerate(segments):
            start = segment[0] / self._frame_overlap - 1
            end = segment[1] / self._frame_overlap + 1
            LPC0_mm[i] = maxmin(LPC0[start:end])
    
            LPC1_max[i] = LPC1[start:end].max()        
            LPC1_mean[i] = LPC1[start:end].mean()
            LPC1_mm[i] = maxmin(LPC1[start:end])
    
            LSF7_min[i] = LSF7[start:end].min()        
            LSF7_mean[i] = LSF7[start:end].mean()
            LSF7_mm[i] = maxmin(LSF7[start:end])
            
            SpectralFlatness_min[i] = SpectralFlatness[start:end].min()
            SpectralFlatness_mean[i] = SpectralFlatness[start:end].mean()
    #        SpectralFlatness_mm[i] = maxmin(SpectralFlatness[start:end])
            
            SSS_centroid_min[i] = SSS_centroid[start:end].min()        
            SSS_centroid_mean[i] = SSS_centroid[start:end].mean()
            SSS_centroid_mm[i] = maxmin(SSS_centroid[start:end])
    
            SSS_spread_min[i] = SSS_spread[start:end].min()        
            SSS_spread_mean[i] = SSS_spread[start:end].mean()
            SSS_spread_mm[i] = maxmin(SSS_spread[start:end])
    
            PerceptualSpread_min[i] = PerceptualSpread[start:end].min()        
            PerceptualSpread_mean[i] = PerceptualSpread[start:end].mean()
            PerceptualSpread_mm[i] = maxmin(PerceptualSpread[start:end])
            
            SpectralSlope_min[i] = SpectralSlope[start:end].min()        
            SpectralSlope_mean[i] = SpectralSlope[start:end].mean()
            SpectralSlope_mm[i] = maxmin(SpectralSlope[start:end])        
    
            PerceptualSharpness_min[i] = PerceptualSharpness[start:end].min()        
            PerceptualSharpness_mean[i] = PerceptualSharpness[start:end].mean()
            PerceptualSharpness_mm[i] = maxmin(PerceptualSharpness[start:end])        
    
            SpectralDecrease_max[i] = SpectralDecrease[start:end].max()        
            SpectralDecrease_mean[i] = SpectralDecrease[start:end].mean()
            SpectralDecrease_mm[i] = maxmin(SpectralDecrease[start:end])  
    
            OBSI0_max[i] = OBSI0[start:end].max()        
            OBSI0_mm[i] = maxmin(OBSI0[start:end])
            
    #        ZCR_mm[i] = maxmin(ZCR[start:end])           
            
            SpectralRolloff_min[i] = SpectralRolloff[start:end].min()        
            SpectralRolloff_mean[i] = SpectralRolloff[start:end].mean()  
            
    #        MFCC2_mm[i] = maxmin(MFCC2[start:end])
    #        MFCC3_mm[i] = maxmin(MFCC3[start:end])
    #        MFCC4_mm[i] = maxmin(MFCC4[start:end])
    #        MFCC5_mm[i] = maxmin(MFCC5[start:end])
    #        MFCC6_mm[i] = maxmin(MFCC6[start:end])
            
            """ Wavelets """
            start_wavelet = segment[0] / 2**wavelet_decomposition_level - 10
            end_wavelet = segment[1] / 2**wavelet_decomposition_level + 10
            wavelets_max_avr_energy[i], wavelets_max_position[i], wavelets_spread[i] = \
                wavelets_calculator.calculate_features(wavelet_coefficients, start_wavelet, end_wavelet)
            
        self.ExtractedFeatures = OrderedDict()
        self.ExtractedFeatures['LPC0_mm'] = LPC0_mm
        self.ExtractedFeatures['LPC1_max'] = LPC1_max
        self.ExtractedFeatures['LPC1_mean'] = LPC1_mean
        self.ExtractedFeatures['LSF7_min'] = LSF7_min
        self.ExtractedFeatures['LSF7_mean'] = LSF7_mean
        self.ExtractedFeatures['LSF7_mm'] = LSF7_mm
        self.ExtractedFeatures['SpectralFlatness_min'] = SpectralFlatness_min
        self.ExtractedFeatures['SpectralFlatness_mean'] = SpectralFlatness_mean
    #    self.ExtractedFeatures['SpectralFlatness_mm'] = SpectralFlatness_mm
        self.ExtractedFeatures['SSS_centroid_min'] = SSS_centroid_min
        self.ExtractedFeatures['SSS_centroid_mean'] = SSS_centroid_mean
        self.ExtractedFeatures['SSS_centroid_mm'] = SSS_centroid_mm
        self.ExtractedFeatures['SSS_spread_min'] = SSS_spread_min
        self.ExtractedFeatures['SSS_spread_mean'] = SSS_spread_mean
        self.ExtractedFeatures['SSS_spread_mm'] = SSS_spread_mm
        self.ExtractedFeatures['PerceptualSpread_min'] = PerceptualSpread_min
        self.ExtractedFeatures['PerceptualSpread_mean'] = PerceptualSpread_mean
        self.ExtractedFeatures['PerceptualSpread_mm'] = PerceptualSpread_mm
        self.ExtractedFeatures['SpectralSlope_min'] = SpectralSlope_min
        self.ExtractedFeatures['SpectralSlope_mean'] = SpectralSlope_mean
        self.ExtractedFeatures['SpectralSlope_mm'] = SpectralSlope_mm
        self.ExtractedFeatures['PerceptualSharpness_min'] = PerceptualSharpness_min
        self.ExtractedFeatures['PerceptualSharpness_mean'] = PerceptualSharpness_mean
        self.ExtractedFeatures['PerceptualSharpness_mm'] = PerceptualSharpness_mm
        self.ExtractedFeatures['SpectralDecrease_max'] = SpectralDecrease_max
        self.ExtractedFeatures['SpectralDecrease_mean'] = SpectralDecrease_mean
        self.ExtractedFeatures['SpectralDecrease_mm'] = SpectralDecrease_mm
        self.ExtractedFeatures['OBSI0_max'] = OBSI0_max
        self.ExtractedFeatures['OBSI0_mm'] = OBSI0_mm
    #    self.ExtractedFeatures['ZCR_mm'] = ZCR_mm
        self.ExtractedFeatures['SpectralRolloff_min'] = SpectralRolloff_min
        self.ExtractedFeatures['SpectralRolloff_mean'] = SpectralRolloff_mean
    #    self.ExtractedFeatures['MFCC2_mm'] = MFCC2_mm
    #    self.ExtractedFeatures['MFCC3_mm'] = MFCC3_mm
    #    self.ExtractedFeatures['MFCC4_mm'] = MFCC4_mm
    #    self.ExtractedFeatures['MFCC5_mm'] = MFCC5_mm
    #    self.ExtractedFeatures['MFCC6_mm'] = MFCC6_mm
        self.ExtractedFeatures['wavelets_max_avr_energy'] = wavelets_max_avr_energy
        self.ExtractedFeatures['wavelets_max_position'] = wavelets_max_position
        self.ExtractedFeatures['wavelets_spread'] = wavelets_spread
        
    def plot_extracted_features(self):
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
        
        plt.show()
        
    def plot(self):
        plt.figure(figsize=(30,60))
        i = 0
        for key, value in self.ExtractedFeatures.iteritems():
            ax = plt.subplot(8,5,i+1)
            plt.plot(value)
            plt.title(key)
            ax.set_xticks([]) 
            i += 1
        plt.show()
        
    def write_to_file(self, file_name):
        fout = open(file_name, 'wb')
        csv_dict_writer = csv.DictWriter(fout, self.Features.keys())
        csv_dict_writer.writeheader()
        csv_dict_writer.writerows()
        
        
def maxmin(array):
    max_val = array.max()
    min_val = array.min()
    return max_val - min_val
    

    


    