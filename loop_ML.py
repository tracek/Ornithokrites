# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:49:27 2013

@author: Lukasz Tracewski

Test module
"""

import os
import pickle
import numpy as np

def find_kiwi(P):
    consecutive = np.zeros(3, dtype='int')
    total = np.zeros(3, dtype='int')
    kiwi_threshold = 4
    kiwi = np.zeros(3, dtype='int')
    
    broken = True
    for i in np.arange(1, len(P)):
        if P[i-1] == P[i]:
            if broken:
                consecutive[P[i]] = 1
            consecutive[P[i]] += 1
            broken = False
        else:
            broken = True
            if P[i-1] > 0 and consecutive[P[i-1]] >= kiwi_threshold:
                kiwi[P[i-1]] += 1
            consecutive[P[i-1]] = 0
            
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
    return result

if __name__ == '__main__':
    data_store = '/home/tracek/Ornitokrites/Recordings/'
    progress = 0.
    
    model = pickle.load(open('model.pkl', 'rb'))
    scaler = pickle.load(open('scaler.pkl', 'rb'))
    
    # male/RFPT-LPA-20111217234502-360-60-KR6.wav N -> M
    # male/RFPT-LPA-20111211221502-840-60-KR6.wav F -> MF
    # male/RFPT-LPA-20111121204503-780-60-KR6.wav N -> M
    # female/RFPT-LPC-20111210001502-600-60-KR7.wav M -> MF
    # female/RFPT-WWMB-20111111213002-780-60-KR3.wav M -> MF
    # female/RFPT-WWMB-20111126214502-180-60-KR3.wav M -> MF
    # female/RFPT-LPA-20111221221502-540-60-KR6.wav M -> MF
    # female/RFPT-WW17-20111109011501-780-60-KR4.wav M -> MF
    # female/RFPT-WW17-20111211221502-780-60-KR5.wav F -> MF
    # female/RFPT-WW13-20111221221502-540-60-KR8.wav F -> MF
#    special = '/home/tracek/Ornitokrites/Recordings/male/RFPT-LPA-20111221221502-540-60-KR6.wav_data.csv'
#    X = np.loadtxt(special, delimiter=',')
#    X = np.nan_to_num(X)
#    X = scaler.transform(X)
#    P = model.predict(X)
#    print find_kiwi(P)
    
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
            result = find_kiwi(P)
        
#            if Y.ndim == 0:
#                if Y == P[0]:
#                    success += 1
#                else:
#                    print 'Baaaaad!'
#                    bad += 1
#                    print target_path
#                    print P[0]
#                    print Y              
#            elif np.array_equal(P, Y):
#                success += 1
#            else:
#                print target_path
#                print P
#                print Y
#                print result
#            print ''
        
#            print target_path
#            print P
#            print Y
#            print result
#            print ''
            
            result_file = open(os.path.join(dirpath, filename + '_result.txt'), 'r')
            truth = result_file.readline()
            result_file.close()
            if truth == result:
                success += 1
            else:
                print filename
                bad += 1
            total += 1
    
    