# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 12:32:13 2014

@author: ltracews
"""

import os
import numpy as np
import matplotlib.pyplot as plt


def pf(feature):
    plt.plot(kiwi[:,feature], '.', label='kiwi')
    plt.plot(not_kiwi[:,feature], '.', label='not_kiwi')
    plt.title(features_list[feature])
    plt.legend(framealpha=0.5)
    
def ph(feature):
    plt.hist(kiwi[:,feature], 60, label='kiwi', alpha=0.5)
    plt.hist(not_kiwi[:,feature], 60, label='not kiwi', alpha=0.5)
    plt.title(features_list[feature])
    plt.legend(framealpha=0.5)
    
def pp(feature):
    plt.subplot(211)
    pf(feature)
    plt.subplot(212)
    ph(feature)
    #plt.savefig(str(feature) + '.png')
    # plt.show()

f = open('features_list.txt', 'r')
features_list = [line.rstrip('\n') for line in f]
f.close()

features_location = 'C:\\Ornithokrites\\Recordings\\'
no_features = 34
X = np.empty(shape=(0, no_features))
Y = np.empty(0, 'int')

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
            Y = np.hstack((Y, target))

not_kiwi_mask = Y == 0        
kiwi_mask = Y > 0
kiwi_female_mask = Y == 1
kiwi_male_mask = Y == 2

not_kiwi = X[not_kiwi_mask]
kiwi = X[kiwi_mask]
kiwi_female = X[kiwi_female_mask]
kiwi_male = X[kiwi_male_mask]

for i in np.arange(no_features):
    pp(i)
    plt.savefig(str(i) + '.png')
    plt.clf()
    