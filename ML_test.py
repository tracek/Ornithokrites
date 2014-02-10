# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 12:32:13 2014

@author: ltracews
"""

import os
import numpy as np

features_location = 'C:\\Ornithokrites\\Recordings\\'
X = np.empty(shape=(0, 34))
Y = np.empty(shape=(0, 1))

L = []

for dirpath, dirnames, filenames in os.walk(features_location):
    for filename in filenames:
        if filename.endswith("_data.csv"):
            path = os.path.join(dirpath, filename)
            data = np.loadtxt(path, delimiter=',')
            X = np.vstack((X, data))
        if filename.endswith("_target.txt"):
            path = os.path.join(dirpath, filename)
            target = np.loadtxt(path, 'int')
            Y = np.vstack((Y, target[None].T))
        

        