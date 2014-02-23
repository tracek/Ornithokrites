# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:25:36 2014

@author: Lukasz Tracewski

Module for identification of kiwi calls
"""

import pickle
import numpy as np

class KiwiFinder(object):
    """ Identification of kiwi calls """
    
    def __init__(self):
        """ Initialize Supervise Vector Machine with Gaussian kernel """
        self._model = pickle.load(open('model.pkl', 'rb'))
        self._scaler = pickle.load(open('scaler.pkl', 'rb'))
        self.KiwiCounts = {'Male': 0, 'Female': 0, 'Male and Female': 0, 'None': 0}
        
    def _look_for_consecutive_calls(self, P, no_consecutive_calls=4):
        """ The most prominent feature of kiwi calls is their repetitive character - use it """
        kiwi = np.zeros(3, dtype='int')
        for i in np.arange(len(P)-no_consecutive_calls):
            # Following will be true if there are at least no_consecutive_calls next to each other
            if np.all(P[i:i+no_consecutive_calls]==P[i]):
                kiwi[P[i]] += 1
        
        # Check border conditions
        if np.all(P[:3]==P[0]):
            kiwi[P[0]] += 1
        if np.all(P[:3]==P[0]):
            kiwi[P[0]] += 1
        if np.all(P[-3:]==P[-1]):
            kiwi[P[-1]] += 1
        if np.all(P[-3:]==P[-1]):
            kiwi[P[-1]] += 1        
                
        if kiwi[1] and kiwi[2] > 0:
            result = 'Male and Female'
        elif kiwi[1] > 0:
            result = 'Female'
        elif kiwi[2] > 0:
            result = 'Male'
        else:
            result = 'None'
            
        self.KiwiCounts[result] += 1
        
        return result        
    
    def find_individual_calls(self, features):
        X = np.nan_to_num(features)
        X = self._scaler.transform(X)
        P = self._model.predict(X)
        return P
        
    def find_kiwi(self, individual_calls):
        result = self._look_for_consecutive_calls(individual_calls)
        if result == 'None':
            # if None were found relax the condition for number of consecutive calls
            result = self._look_for_consecutive_calls(individual_calls,3)
        return result
        
        