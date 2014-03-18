# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 21:41:18 2014

@author: Lukasz Tracewski
"""

from __future__ import division
import numpy as np
from collections import namedtuple


Kiwicandidate = namedtuple('Kiwicandidate','start end density')

def contiguous_regions(condition):
    d = np.diff(condition)  # Where the condition changes
    idx, = d.nonzero()  # Get the indices
    idx += 1  # We were lagging behind the condition
    if condition[0]:  # Handle border conditions
        idx = np.r_[0, idx]
    if condition[-1]:
        idx = np.r_[idx, condition.size]
    idx.shape = (-1, 2)
    return idx
    
def find_candidates(condition, segments, rate, min_length, min_calls_density):
    candidates = []    
    result = contiguous_regions(condition)
    for start, end in result:
        length = end - start
        if length >= min_length:
            region_start = segments[start][0]
            region_end = segments[start + length - 1][1]
            calls_density = (rate * length) / (region_end - region_start)
            if calls_density > min_calls_density:
                candidates.append(Kiwicandidate(region_start, region_end, calls_density))
    return candidates

if __name__ == '__main__':
    seg1 = [(0, 8200),
         (8000, 16200),
         (16000, 24200),
         (24000, 32200),
         (32000, 40200),
         (40000, 48200),
         (48000, 56200),
         (56000, 64200),
         (64000, 72200),
         (72000, 80200),
         (80000, 88200),
         (88000, 96200),
         (96000, 104200),
         (104000, 112200),
         (112000, 120200),
         (120000, 128200),
         (128000, 136200),
         (136000, 144200),
         (144000, 152200)]
         
    kiwi1 = np.array([1,1,0,1,2,2,2,1,1,1,1,0,0,1,2,2,1,1,1])
    
    kiwi2 = np.array([1,1,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0])
    kiwi3 = np.array([2,2,0,2,2,2,2,2,1,2,1,1,1,1,1,0,1,1,0,0,0,2])
    kiwi4 = np.array([2,2,0,2,2,2,2,2,2,2,0,0])

    min_length = 4
    min_calls_density = 0.5
    rate = 8000
    
    females = find_candidates(kiwi1 == 1, seg1, 8000, min_length, min_calls_density)
    males = find_candidates(kiwi1 == 2, seg1, 8000, min_length, min_calls_density)
    
    