# -*- coding: utf-8 -*-
"""
Created on Mon Dec 02 12:07:49 2013

@author: ltracews
"""

import os
import sys
import itertools
import numpy as np
import matplotlib.pyplot as plt
import yaafelib


class FeatureExtractor(object):

    def __init__(self, app_config, rate):
        self.ExtractedFeaturesList = ['LPC1_mean', 'LSF7_min', 'SpectralFlatness_min',
                                      'SSS_centroid_min', 'SSS_spread_min', 'PerceptualSpread_min',
                                      'SpectralSlope_min', 'PerceptualSharpness_min', 'SpectralDecrease_max',
                                      'OBSI0_mm', 'SpectralRolloff_min']
        self._rate = rate
        feature_plan = yaafelib.FeaturePlan(sample_rate=rate)
        feature_plan_path = os.path.join(app_config.program_directory, 'features.config')
        success = feature_plan.loadFeaturePlan(feature_plan_path)
        if not success:
            sys.exit('Feature plan not loaded correctly')
        self._engine = yaafelib.Engine()
        self._engine.load(feature_plan.getDataFlow())

    def process(self, signal, segments, wavelet_decomposition_level=6, frame_overlap=512, wavelet_type='sym10'):
        """ Extract features """

        self._signal = signal
        self._segments = segments

        """ Calculate spectral and temporal features """

        self.Features = self._engine.processAudio(np.array([signal.astype('float64')]))

        """ Initialize wavelet features
            Based on "Wavelets in Recognition of Bird Sounds" by A. Selin et al.
            EURASIP Journal on Advances in Signal Processing 2007, 2007:051806 """
#        wavelets_calculator = wavelets.Wavelets(wavelet_type)
#        wavelet_coefficients = wavelets_calculator.decompose(signal, wavelet_decomposition_level)
#
        no_segments = len(segments)

        self.ExtractedFeatures = np.zeros(shape=(no_segments, len(self.ExtractedFeaturesList)))

        LPC1 = self.Features['LPC'][:, 1]
        LSF7 = self.Features['LSF'][:, 7]
        SpectralFlatness = self.Features['SpectralFlatness']
        SSS_centroid = self.Features['SpectralShapeStatistics'][:, 0]
        SSS_spread = self.Features['SpectralShapeStatistics'][:, 1]
        PerceptualSpread = self.Features['PerceptualSpread']
        SpectralSlope = self.Features['SpectralSlope']
        PerceptualSharpness = self.Features['PerceptualSharpness']
        SpectralDecrease = self.Features['SpectralDecrease']
        OBSI0 = self.Features['OBSI'][:, 0]
        SpectralRolloff = self.Features['SpectralRolloff']

        for i, segment in enumerate(segments):
            start = int(segment[0] / frame_overlap)
            end = int(segment[1] / frame_overlap)

            self.ExtractedFeatures[i, 0] = LPC1[start:end].mean()
            self.ExtractedFeatures[i, 1] = LSF7[start:end].min()
            self.ExtractedFeatures[i, 2] = SpectralFlatness[start:end].min()
            self.ExtractedFeatures[i, 3] = SSS_centroid[start:end].min()
            self.ExtractedFeatures[i, 4] = SSS_spread[start:end].min()
            self.ExtractedFeatures[i, 5] = PerceptualSpread[start:end].min()
            self.ExtractedFeatures[i, 6] = SpectralSlope[start:end].min()
            self.ExtractedFeatures[i, 7] = PerceptualSharpness[start:end].min()
            self.ExtractedFeatures[i, 8] = SpectralDecrease[start:end].max()
            self.ExtractedFeatures[i, 9] = maxmin(OBSI0[start:end])
            self.ExtractedFeatures[i, 10] = SpectralRolloff[start:end].min()

        return self.ExtractedFeatures

    def plot_features(self, file_name=''):
        plt.figure(figsize=(12, 50))
        n = 12
        nx = 1

        plt.subplot(n, nx, 0)
        plt.specgram(self._signal, NFFT=2**11, Fs=self._rate)
        for start, end in self._segments:
            start /= self._rate
            end /= self._rate
            plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2)
            plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)

        plt.subplot(n, nx, 1)
        plt.title('SpectralFlatness')
        plt.plot(self.Features['SpectralFlatness'])

        plt.subplot(n, nx, 2)
        plt.title('SpectralShapeStatistics - centroid')
        plt.plot(self.Features['SpectralShapeStatistics'][:, 0])

        plt.subplot(n, nx, 3)
        plt.title('SpectralShapeStatistics - spread')
        plt.plot(self.Features['SpectralShapeStatistics'][:, 1])

        plt.subplot(n, nx, 4)
        plt.title('PerceptualSpread')
        plt.plot(self.Features['PerceptualSpread'])

        plt.subplot(n, nx, 5)
        plt.title('SpectralSlope')
        plt.plot(self.Features['SpectralSlope'])

        plt.subplot(n, nx, 6)
        plt.title('PerceptualSharpness')
        plt.plot(self.Features['PerceptualSharpness'])

        plt.subplot(n, nx, 7)
        plt.title('SpectralDecrease')
        plt.plot(self.Features['SpectralDecrease'])

        plt.subplot(n, nx, 8)
        plt.title('OBSI - 0')
        plt.plot(self.Features['OBSI'][:, 0])

        plt.subplot(n, nx, 9)
        plt.title('LPC - 1')
        plt.plot(self.Features['LPC'][:, 1])

        plt.subplot(n, nx, 10)
        plt.title('SpectralRolloff')
        plt.plot(self.Features['SpectralRolloff'])

        plt.subplot(n, nx, 11)
        plt.title('LSF - 7')
        plt.plot(self.Features['LSF'][:, 7])

        if file_name:
            plt.savefig(file_name + '.png')
            plt.clf()
        else:
            plt.show()

    def plot_extracted_features(self, file_name=''):
        plt.figure(figsize=(30, 60))
        no_features = np.shape(self.ExtractedFeatures)[1]
        for column in np.arange(no_features):
            ax = plt.subplot(7, 5, column + 1)
            plt.plot(self.ExtractedFeatures[:, column])
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

    def read_extracted_features_from_csv(self, file_name):
        return np.loadtxt(file_name, delimiter=',')

    def read_target(self, file_name):
        return np.loadtxt(file_name)


def maxmin(array):
    max_val = array.max()
    min_val = array.min()
    return max_val - min_val
