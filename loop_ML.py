# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:49:27 2013

@author: Lukasz Tracewski

Test module
"""

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt


data_store = '/home/tracek/Ornitokrites/Recordings/'
progress = 0.



model = pickle.load(open('model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))

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
        X = scaler.transform(X)
        P = model.predict(X)
        
        target_path = os.path.join(dirpath, filename + '_target.txt') 
        Y = np.loadtxt(target_path, 'int')
        
        consecutive = np.zeros(3, dtype='int')
        total = np.zeros(3, dtype='int')
        kiwi_threshold = 4
        kiwi = np.zeros(3, dtype='int')
        
        current = P[0]
        consecutive[current] += 1
        broken = True
        for i in np.arange(1, len(P)):
            total[P[i]] += 1
            if current == P[i]:
                consecutive[P[i]] += 1
                broken = False
            else:
                broken = True
                if P[i-1] > 0 and consecutive[P[i-1]] >= kiwi_threshold:
                    kiwi[P[i-1]] += 1
                    consecutive[P[i-1]] = 0
                current = P[i]
                
        if not broken and consecutive[P[i]] >= kiwi_threshold:
            kiwi[P[i]] += 1
                
        if kiwi[1] and kiwi[2] > 0:
            result = 'Male and Female'
        elif kiwi[1] > 0:
            result = 'Female'
        elif kiwi[2] > 0:
            result = 'Male'
        else:
            result = 'None'
    
        if Y.ndim == 0:
            if Y == P[0]:
                success += 1
            else:
                print 'Baaaaad!'
                bad += 1
                print target_path
                print P[0]
                print Y              
        elif np.array_equal(P, Y):
            success += 1
        else:
            print target_path
            print P
            print Y
            print result
        print ''  

special = '/home/tracek/Ornitokrites/Recordings/male/RFPT-LPA-20111121204503-780-60-KR6.wav_data.csv'
X = np.loadtxt(special, delimiter=',')
X = np.nan_to_num(X)
X = scaler.transform(X)
P = model.predict(X)