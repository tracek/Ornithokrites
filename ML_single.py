# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 13:43:12 2014

@author: Lukasz Tracewski
"""

import pickle
import numpy as np
#import Tkinter, tkFileDialog
#root = Tkinter.Tk()
#root.withdraw()
#data_path = tkFileDialog.askopenfilename()

def look_for_consecutive_calls(P, no_consecutive_calls=4):
    consecutive = np.zeros(3, dtype='int')
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
            if P[i-1] > 0 and consecutive[P[i-1]] >= no_consecutive_calls:
                kiwi[P[i-1]] += 1
            consecutive[P[i-1]] = 0
            
    if not broken and consecutive[P[i]] >= no_consecutive_calls:
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
    result = look_for_consecutive_calls(P)
    if result == 'None':
        result = look_for_consecutive_calls(P,3)
    return result

recording = '/home/tracek/Ornitokrites/Recordings/female/RFPT-LPA-20111221221502-540-60-KR6.wav'
result_file = open(recording + '_result.txt', 'r')
truth = result_file.readline()
result_file.close()

model = pickle.load(open('model2.pkl', 'rb'))
scaler = pickle.load(open('scaler2.pkl', 'rb'))

Y = np.loadtxt(recording + '_target.txt', 'int')
X = np.loadtxt(recording + '_data.csv', delimiter=',')
X = np.nan_to_num(X)
X = scaler.transform(X)
P = model.predict(X)

print find_kiwi(P) + ' --> ' + truth
print P
print Y