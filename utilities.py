# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 21:41:18 2014

@author: Lukasz Tracewski
"""

import np


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
