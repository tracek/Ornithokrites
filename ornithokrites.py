#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:50:43 2014

@author: Lukasz Tracewski

Identification of kiwi calls from audio recordings - main module.
"""

import multiprocessing
import configuration
import reporting
import noise_reduction
import features
import identification
import s3connection

class Ornithokrites(object):
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
        reporter.cleanup()
        
class ParallelOrnithokrites(object):
    def __init__(self):
        app_config = configuration.Configurator().parse_arguments()
        reporter = reporting.Reporter(location=app_config.data_store, 
                                      write_to_stdout=app_config.write_stdout)
        recordings_buffer_size = app_config.no_processes * 4
        
        self.recordings_q = multiprocessing.Queue(recordings_buffer_size)
        self.output_q = multiprocessing.Queue()

        self.process_in = multiprocessing.Process(target=s3connection.RecordingsFetcher().get_recordings, 
                                                  args=(app_config, self.recordings_q))
        self.process_out = multiprocessing.Process(target=reporter.write_results_parallel,
                                                   args=(app_config, self.output_q))
        self.process_kiwi = [multiprocessing.Process(target=self.process, args=()) for i in range(app_config.no_processes)]                                   
    
    def run(self):      
        self.process_in.start()
        self.process_out.start()
        for kiwi in self.process_kiwi:
            kiwi.start()
        self.process_in.join()
        for kiwi in self.process_kiwi:
            kiwi.join()
        self.process_out.join()
        
    def process(self):
        kiwi_finder = identification.KiwiFinder()
        noise_remover = noise_reduction.NoiseRemover()
        for rate, sample, sample_name in iter(self.recordings_q.get, "STOP"): 
            try:
                filtered_sample = noise_remover.remove_noise(sample, rate)
            except:
                filtered_sample = sample
        
            segmented_sounds = noise_remover.segmentator.get_segmented_sounds()
            
            feature_extractor = features.FeatureExtractor()
            extracted_features = feature_extractor.process(filtered_sample, rate, segmented_sounds)
            
            kiwi_calls = kiwi_finder.find_individual_calls(extracted_features)
            result_per_file = kiwi_finder.find_kiwi(kiwi_calls)
            self.output_q.put((result_per_file, kiwi_calls, sample_name, filtered_sample, rate, segmented_sounds))
        self.output_q.put("STOP")
            

if __name__ == '__main__':
    ParallelOrnithokrites().run()
