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
    """
    Synchronous version. All steps are done in sequence: a single wave file is acquired and then
    processed. 
    """
    def __init__(self, app_config):
        self.app_config = app_config
        self.reporter = reporting.Reporter(app_config)
        self.kiwi_finder = identification.KiwiFinder()
        self.noise_remover = noise_reduction.NoiseRemover()
        self.fetcher = s3connection.RecordingsFetcher()        
    def run(self):
        for rate, sample, sample_name in self.fetcher.get_next_recording(data_store=app_config.data_store, 
                                                                         bucket_name=app_config.bucket): 
            try:
                filtered_sample = self.noise_remover.remove_noise(sample, rate)
            except:
                filtered_sample = sample
        
            segmented_sounds = self.noise_remover.segmentator.get_segmented_sounds()
            
            feature_extractor = features.FeatureExtractor()
            extracted_features = feature_extractor.process(filtered_sample, rate, segmented_sounds)
            
            kiwi_calls = self.kiwi_finder.find_individual_calls(extracted_features)
            result_per_file = self.kiwi_finder.find_kiwi(kiwi_calls)
            self.reporter.write_results(result_per_file, kiwi_calls, sample_name, filtered_sample, 
                                        rate, segmented_sounds)
        self.reporter.cleanup()
        
class ParallelOrnithokrites(object):
    """
    Asynchrounous version. Recordings are put inside a queue and then passed to workers that will
    handle the processing. Each worker shall submit its results to an output queue. 
    """
    def __init__(self, app_config):
        self.app_config = app_config
        reporter = reporting.Reporter(app_config)
        recordings_buffer_size = app_config.no_processes * 4 # only this number of recordings will be acquired
        
        self.recordings_q = multiprocessing.Queue(recordings_buffer_size) # limited size of a queue
        self.output_q = multiprocessing.Queue()

        self.process_in = multiprocessing.Process(target=s3connection.RecordingsFetcher().get_recordings, 
                                                  args=(app_config, self.recordings_q))
        self.process_out = multiprocessing.Process(target=reporter.write_results_parallel,
                                                   args=(self.output_q,))
        self.process_kiwi = [multiprocessing.Process(target=self.worker, args=()) for i in range(app_config.no_processes)]                                   
    
    def run(self):      
        self.process_in.start()
        self.process_out.start()
        for kiwi in self.process_kiwi:
            kiwi.start()
        self.process_in.join()
        for kiwi in self.process_kiwi:
            kiwi.join()
        self.process_out.join()
        
    def worker(self):
        kiwi_finder = identification.KiwiFinder(self.app_config)
        noise_remover = noise_reduction.NoiseRemover()
        
        for rate, sample, sample_name in iter(self.recordings_q.get, "STOP"): 
            try:
                filtered_sample = noise_remover.remove_noise(sample, rate)
            except:
                filtered_sample = sample
        
            segmented_sounds = noise_remover.segmentator.get_segmented_sounds()
            feature_extractor = features.FeatureExtractor(self.app_config, rate)    
            extracted_features = feature_extractor.process(signal=filtered_sample, segments=segmented_sounds)
            
            kiwi_calls = kiwi_finder.find_individual_calls(extracted_features)
            result_per_file = kiwi_finder.find_kiwi(kiwi_calls)
            self.output_q.put((result_per_file, kiwi_calls, sample_name, filtered_sample, rate, segmented_sounds))
        self.output_q.put("STOP")
            

if __name__ == '__main__':
    app_config = configuration.Configurator().parse_arguments()
    if app_config.synchronous:
        Ornithokrites(app_config).run()
    else:
        ParallelOrnithokrites(app_config).run()
        
