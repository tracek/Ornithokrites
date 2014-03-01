#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:50:43 2014

@author: Lukasz Tracewski

Identification of kiwi calls from audio recordings - main module.
"""

import configuration
import reporting
import recordings_io
import noise_reduction
import features
import identification
import s3connection


class MassiveOrnithokrites(object):
    """ This class is meant as a replacement of original Ornithokrites. Purpose is to make processing
        of data on-demand: file is not downloaded unless at given moment it needs to be processed. 
        Another advantage is that we can enable parallel processing: there are no reasons why we should
        not work in parallel on number of samples equal to number of CPU cores """

    def run(self):    
        app_config = configuration.Configurator().parse_arguments()
        reporter = reporting.Reporter(location=app_config.data_store, write_to_stdout=app_config.write_stdout)
        kiwi_finder = identification.KiwiFinder()
        noise_remover = noise_reduction.NoiseRemover()
        fetcher = s3connection.RecordingsFetcher()
    
        for rate, sample, sample_name in fetcher.get_next_recording(data_store=app_config.data_store, 
                                                                    bucket_name=app_config.bucket): 
            try:
                filtered_sample = noise_remover.remove_noise(sample, rate)
            except:
                filtered_sample = sample
        
            segmented_sounds = noise_remover.segmentator.get_segmented_sounds()
            
            feature_extractor = features.FeatureExtractor()
            extracted_features = feature_extractor.process(filtered_sample, rate, segmented_sounds)
            
            kiwi_calls = kiwi_finder.find_individual_calls(extracted_features)
            result_per_file = kiwi_finder.find_kiwi(kiwi_calls)
            reporter.write_results(result_per_file, kiwi_calls, sample_name, filtered_sample, 
                                   rate, segmented_sounds, app_config.keep_data)


class Ornithokrites(object):
    
    def run(self):
        app_config = configuration.Configurator().parse_arguments()
        reporter = reporting.Reporter(location=app_config.data_store, write_to_stdout=app_config.write_stdout)
        walker = recordings_io.get_recordings_walker(data_store=app_config.data_store, bucket=app_config.bucket)
        kiwi_finder = identification.KiwiFinder()
        
        for rate, sample, sample_name in walker.read_wave(): 
            noise_remover = noise_reduction.NoiseRemover()
            try:
                filtered_sample = noise_remover.remove_noise(sample, rate)
            except:
                filtered_sample = sample
        
            segmented_sounds = noise_remover.segmentator.get_segmented_sounds()
            
            feature_extractor = features.FeatureExtractor()
            extracted_features = feature_extractor.process(filtered_sample, rate, segmented_sounds)
            
            kiwi_calls = kiwi_finder.find_individual_calls(extracted_features)
            result_per_file = kiwi_finder.find_kiwi(kiwi_calls)
            reporter.write_results(result_per_file, kiwi_calls, sample_name, filtered_sample, rate, segmented_sounds)

        reporter.cleanup()

if __name__ == '__main__':
    MassiveOrnithokrites().run()
