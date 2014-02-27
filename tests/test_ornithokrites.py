# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 07:59:13 2014

@author: Lukasz Tracewski
"""

import os
import sys
import logging
import nose.tools as nt



@nt.nottest
class test_ornithokrites(object):
    
    def setup_test_configuration(self):
        print 'Full Ornithokrites test - will take a while.'
        from recordings_io import Walker
        del sys.argv[2] # remove -s coming from the nose
        storage_location = './tests/TestRecordings/'
        walker = Walker(storage_location)
        expected_number_of_recordings = 206
        if walker.count == expected_number_of_recordings:
            # 
            print 'Assuming we already have the kiwicalldata - no need to download it again'
            sys.argv = [__file__, '-d' + storage_location, '--stdout']
        else:
            # Assume data is not there
            bucket_name = 'kiwicalldata'
            sys.argv = [__file__, '-b' + bucket_name, '-d' + storage_location, '--stdout']
        handler = logging.FileHandler('test_result.txt', 'w')
        log = logging.getLogger('log.html')
        log.addHandler(handler)
        
        
    def test_get_recordings_and_identify_kiwi(self): 
        from ornithokrites import Ornithokrites        
        Ornithokrites().run()
        with open('expected_results.txt', 'r') as expected_results:
            with open('2.txt', 'r') as file2:
                same = set(expected_results).difference(file2)
                
    def teardown_test_ornithokrites(self):
        print 'Full Ornithokrites test completed'
        
        