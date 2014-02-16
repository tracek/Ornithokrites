# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:49:27 2013

@author: Lukasz Tracewski

Test module
"""

import numpy as np
import matplotlib.pyplot as plt
import os

data_store = '/home/tracek/Ornitokrites/Recordings/'
progress = 0.

from sklearn import preprocessing
import pickle

file_model = open('model.pkl', 'rb')
model = pickle.load(file_model)
file_model.close()

total = 0
files = 0
success = 0
bad = 0

for dirpath, dirnames, filenames in os.walk(data_store):
    for filename in [f for f in filenames if f.endswith(".wav")]:
        total += 1
        data_path = os.path.join(dirpath, filename + '_data.csv')
        X = np.loadtxt(data_path, delimiter=',')
        X = np.nan_to_num(X)
        X = preprocessing.scale(X)
        P = clf.predict(X)
        
        target_path = os.path.join(dirpath, filename + '_target.txt') 
        Y = np.loadtxt(target_path, 'int')
        break
    
        if Y.ndim == 0:
            if Y == P[0]:
                success += 1
            else:
                bad += 1
                print filename
                print ''                
        elif np.array_equal(P, Y):
            success += 1
        else:
            print filename
            wrong = []
            for i in np.arange(len(Y)):
                if P[i] != Y[i]:
                    wrong.append(i)
                    bad += 1
            print wrong
            print ''