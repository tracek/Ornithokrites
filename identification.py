# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:25:36 2014

@author: Lukasz Tracewski

Module for identification of kiwi calls
"""

import os
import pickle
import numpy as np
from collections import namedtuple
from utilities import contiguous_regions

Candidate = namedtuple('Candidate', 'start end')


class KiwiFinder(object):
    """ Identification of kiwi calls """

    def __init__(self, app_config):
        """ Initialize Supervise Vector Machine with Gaussian kernel """
        model_path = os.path.join(app_config.program_directory, 'model.pkl')
        scaler_path = os.path.join(app_config.program_directory, 'scaler.pkl')
        with open(model_path, 'rb') as model_loader, open(scaler_path, 'rb') as scaler_loader:
            self._model = pickle.load(model_loader)
            self._scaler = pickle.load(scaler_loader)
        self._min_calls_density = 0.6
        self._min_no_border_calls = 3

    def find_individual_calls(self, features):
        X = np.nan_to_num(features)
        X = self._scaler.transform(X)
        P = self._model.predict(X)
        return P

    def find_kiwi_regions(self, condition, segments, rate, min_no_ind_calls):
        candidates = []
        result = contiguous_regions(condition)
        for start, end in result:
            length = end - start
            if length >= min_no_ind_calls:
                region_start = segments[start][0]
                region_end = segments[start + length - 1][1]
                if self._density_above_threshold(region_start, region_end, length, rate):
                    candidates.append(Candidate(region_start, region_end))
                else:
                    for i in np.arange(length - min_no_ind_calls):
                        region_start = i
                        region_end = i + min_no_ind_calls
                        if self._density_above_threshold(region_start, region_end, min_no_ind_calls, rate):
                            candidates.append(Candidate(region_start, region_end))
        return candidates

    def find_candidates(self, gender, individual_calls, segments, rate, min_no_ind_calls):
        if gender == 'Female':
            gender = 1
        elif gender == 'Male':
            gender = 2
        kiwi = []
        kiwi += self.find_kiwi_regions(individual_calls == gender, segments, rate, min_no_ind_calls)
        kiwi += self.find_kiwi_regions(individual_calls[0:self._min_no_border_calls] == gender, segments,
                                       rate, self._min_no_border_calls)
        kiwi += self.find_kiwi_regions(individual_calls[-self._min_no_border_calls:] == gender, segments,
                                       rate, self._min_no_border_calls)
        return kiwi

    def _density_above_threshold(self, region_start, region_end, length, rate):
        calls_density = (rate * length) / (region_end - region_start)
        if calls_density > self._min_calls_density:
            return True
        else:
            return False

    def find_kiwi(self, individual_calls, segments, rate):
        females = self.find_candidates('Female', individual_calls, segments, rate, min_no_ind_calls=4)
        males = self.find_candidates('Male', individual_calls, segments, rate, min_no_ind_calls=4)
        if not males and not females:
            females = self.find_candidates('Female', individual_calls, segments, rate, min_no_ind_calls=3)
            males = self.find_candidates('Male', individual_calls, segments, rate, min_no_ind_calls=3)
        if males and females:
            return 'Male and Female'
        elif males:
            return 'Male'
        elif females:
            return 'Female'
        else:
            return 'None'
