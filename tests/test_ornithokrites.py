# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 07:59:13 2014

@author: Lukasz Tracewski
"""

import sys
import json
import logging
import nose.tools as nt
from recordings_io import Walker
from ornithokrites import Ornithokrites   

@nt.nottest
class test_ornithokrites(object):
    
    def setup_test_configuration(self):
        print 'Full Ornithokrites test - will take a while.'
        
        self.results_test = 'results_test.out'
        self.results_expected = 'results_expected.in'
        
        del sys.argv[2] # remove -s coming from the nose
        storage_location = './tests/TestRecordings/'
        walker = Walker(storage_location)
        expected_number_of_recordings = 190 # number of unique recordings in kiwicalldata
        if walker.count == expected_number_of_recordings:
            # 
            print 'Assuming we already have the kiwicalldata - no need to download it again'
            sys.argv = [__file__, '-d' + storage_location, '--stdout']
#        else:
#            # Assume data is not there
#            bucket_name = 'kiwicalldata'
#            sys.argv = [__file__, '-b' + bucket_name, '-d' + storage_location, '--stdout']
            
        handler = logging.FileHandler(self.results_test, 'w')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)        
        log = logging.getLogger('log.html')
        log.addHandler(handler)
        
        
    def test_get_recordings_and_identify_kiwi(self):           
        Ornithokrites().run()
        
        with open(self.results_expected, 'r') as results_expected:
            results_expected_dict = json.load(results_expected)
        with open(self.results_test, 'r') as results_test:
            results_test_list = results_test.read().splitlines()
                
        test_dict = {}
        for entry in results_test_list:
            filename, result = entry.split(' ',1)
            test_dict[filename] = result
        
        nt.assert_dict_equal(results_expected_dict, test_dict)
                
    def teardown_test_ornithokrites(self):
        print 'Full Ornithokrites test completed'
        
        