#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:50:43 2014

@author: Lukasz Tracewski

Identification of kiwi calls from audio recordings - main module.
"""

import reporting
import recordings_io
import noise_reduction
import features
import identification

walker = recordings_io.get_recordings_walker()
kiwi_finder = identification.KiwiFinder()

for rate, sample, sample_name in walker.read_wave(): 
    noise_remover = noise_reduction.NoiseRemover()
    try:
        filtered_sample = noise_remover.remove_noise(sample, rate)
    except ValueError:
        filtered_sample = sample

    segmented_sounds = noise_remover.segmentator.get_segmented_sounds()
    
    feature_extractor = features.FeatureExtractor()
    feature_extractor.process(filtered_sample, rate, segmented_sounds)
    extracted_features = feature_extractor.ExtractedFeatures
    
    kiwi_calls = kiwi_finder.find_individual_calls(extracted_features)
    result_per_file = kiwi_finder.find_kiwi(kiwi_calls)
    reporting.write_results(result_per_file, kiwi_calls, sample_name, filtered_sample, rate, segmented_sounds)

reporting.remove_loggers()