# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:49:27 2013

@author: Lukasz Tracewski

Test module
"""

from __future__ import division
import os
import pickle
import numpy as np

def look_for_consecutive_calls2(P, no_consecutive_calls=4):
    kiwi = np.zeros(3, dtype='int')
    for i in np.arange(len(P)-no_consecutive_calls):
        if np.all(P[i:i+no_consecutive_calls]==P[i]):
            kiwi[P[i]] += 1
            
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
    return result

    
def find_kiwi(P):
    result = look_for_consecutive_calls2(P)
    if result == 'None':
        result = look_for_consecutive_calls2(P,3)
    return result
    
def write_results(name, results):
    f = open(name, 'w')
    for result in results:
        f.write(result + '\n')
    f.close()

if __name__ == '__main__':
    data_store = '/home/tracek/Ornitokrites/Recordings/'
    progress = 0.
    
    model = pickle.load(open('model.pkl', 'rb'))
    scaler = pickle.load(open('scaler.pkl', 'rb'))
    
    # /home/tracek/Ornitokrites/Recordings/male/RFPT-LPA-20111128233002-120-60-KR6.wav
    
#    X = np.loadtxt(special, delimiter=',')
#    X = np.nan_to_num(X)
#    X = scaler.transform(X)
#    P = model.predict(X)
#    print find_kiwi(P)
    
    total = 0
    success = 0
    bad = 0
    
    report = {'Male': 0, 'Female': 0, 'Male and Female': 0, 'None': 0}
    
    Males = []
    Females = []
    MF = []
    NotKiwi = []
    
    for dirpath, dirnames, filenames in os.walk(data_store):
        for filename in [f for f in filenames if f.endswith(".wav")]:
            data_path = os.path.join(dirpath, filename + '_data.csv')
            X = np.loadtxt(data_path, delimiter=',')
            X = np.nan_to_num(X)
            X = scaler.transform(X)
            P = model.predict(X)
            
            target_path = os.path.join(dirpath, filename + '_target.txt') 
            try:
                Y = np.loadtxt(target_path, 'int')
            except:
                np.savetxt(os.path.join(dirpath, filename + '_targetP.txt') , P, '%d')
                open(os.path.join(dirpath, filename + '_result.txt'),'w').close()
                raise
                
                
            result = find_kiwi(P)
            
            result_file = open(os.path.join(dirpath, filename + '_result.txt'), 'r')
            truth = result_file.readline()
            result_file.close()
            if truth == result:
                report[result] += 1
                success += 1
                
                name = os.path.join(dirpath, filename)
                name = name.replace('/home/tracek/Ornitokrites/Recordings/','')
                
#                print target_path
#                print P
#                print Y
#                
                if result == 'Male':
                    Males.append(name)
                elif result == 'Female':
                    Females.append(name)
                elif result == 'Male and Female':
                    MF.append(name)
                elif result == 'None':
                    NotKiwi.append(name)
                else:
                    raise ValueError('Unknown result: %s in file %s' % (result, result_file))
                    
            else:
                print target_path
                print P
                print Y
                print result + ' --> ' + truth
                print ''
                bad += 1
            total += 1
            
    write_results('Males.out', Males)
    write_results('Females.out', Females)
    write_results('MalesFemales.out', MF)
    write_results('NotKiwi.out', NotKiwi)
            
    print 100.0 * success / total
    
    