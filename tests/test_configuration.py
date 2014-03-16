# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 11:12:39 2014

@author: Lukasz Tracewski
"""
import sys
import nose.tools as nt
from configuration import Configurator

class test_configuration(object):
    
    def setup_test_configuration(self):
        del sys.argv[2] # remove -s coming from the nose
    
    def test_user_provided_bucket_and_store(self):
        bucket_name = 'mybucket'
        storage_location = 'mydatastore'
        sys.argv = [__file__, '-b' + bucket_name, '-d' + storage_location]
        configurator = Configurator()
        app_config = configurator.parse_arguments()
        nt.assert_equal(app_config.bucket, bucket_name)
        nt.assert_equal(app_config.data_store, storage_location)
        nt.assert_false(app_config.write_stdout)
        
    def test_user_provided_bucket(self):
        bucket_name = 'mybucket'
        web_store =  '/var/www/results/'
        sys.argv = [__file__, '-b' + bucket_name]
        configurator = Configurator()
        app_config = configurator.parse_arguments()
        nt.assert_equal(app_config.bucket, bucket_name)
        nt.assert_equal(app_config.data_store, web_store)
        nt.assert_false(app_config.write_stdout)
        
    def test_user_provided_store(self):
        storage_location = 'mydatastore'
        sys.argv = [__file__, '-d' + storage_location]
        configurator = Configurator()
        app_config = configurator.parse_arguments()
        nt.assert_is_none(app_config.bucket)
        nt.assert_equal(app_config.data_store, storage_location)
        nt.assert_false(app_config.write_stdout)
        
    def test_user_provided_store_and_stdout(self):
        storage_location = 'mydatastore'
        sys.argv = [__file__, '-d' + storage_location, '--stdout']
        configurator = Configurator()
        app_config = configurator.parse_arguments()
        nt.assert_is_none(app_config.bucket)
        nt.assert_equal(app_config.data_store, storage_location)
        nt.assert_true(app_config.write_stdout)        

        
