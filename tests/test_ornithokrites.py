# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 07:59:13 2014

@author: Lukasz Tracewski
"""

import sys, os
import csv
import logging
import nose.tools as nt

# @nt.nottest
class test_ornithokrites(object):
    
    def setup_test_configuration(self):
        print 'Full Ornithokrites test - will take a while.'
        from recordings_io import Walker
        del sys.argv[2] # remove -s coming from the nose
        storage_location = './tests/TestRec/'
        walker = Walker(storage_location)
        expected_number_of_recordings = 190 # number of unique recordings in kiwicalldata
        if walker.count() == expected_number_of_recordings:
            # 
            print 'Assuming we already have the kiwicalldata - no need to download it again'
            sys.argv = [__file__, '-d' + storage_location, '--stdout', '-p 4']
        else:
            # Assume data is not there
            bucket_name = 'kiwicalldata'
            sys.argv = [__file__, '-b' + bucket_name, '-d' + storage_location, '--stdout']
        print 'completed'
        
    def test_get_recordings_and_identify_kiwi(self):
        from configuration import Configurator
        from ornithokrites import ParallelOrnithokrites   
        
        results_test = './tests/results_test.out'
        results_expected = './tests/results_expected.csv'
                
        app_config = Configurator().parse_arguments()
        ornithokrites = ParallelOrnithokrites(app_config)
        
        handler = logging.FileHandler(results_test, 'w')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)        
        log = logging.getLogger('log.html')
        log.addHandler(handler)        
        
        ornithokrites.run()
        
        results_expected_dict = load_expected_results(results_expected)
        results_text_dict = load_results(results_test)

        nt.assert_dict_contains_subset(results_expected_dict, results_text_dict)


def load_expected_results(path):
    with open(path, 'rb') as file_in:
        results = dict(x for x in csv.reader(file_in))
    return results
    
def load_results(path):
    accepted_results = {'None', 'Female', 'Male', 'Male and Female'}
    with open(path, 'r') as results_test:
        results_test_list = results_test.read().splitlines()
            
    test_dict = {}
    for entry in results_test_list:
        filename, result = entry.split(' ',1)
        filename = os.path.basename(filename).replace(':','')
        if result in accepted_results:
            test_dict[filename] = result    
    
    return test_dict
    
if __name__ == '__main__':
    results_expected_dict = load_expected_results('results_expected.csv')
    results_text_dict = load_results('results_test.out')
    nt.assert_dict_contains_subset(results_text_dict, results_expected_dict)