# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 07:05:19 2014

@author: tracek
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 12:32:13 2014

@author: ltracews
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn import svm



def pf(data1, label1, data2, label2, feature, features_list):
    plt.plot(data1[:,feature], '.', label=label1)
    plt.plot(data2[:,feature], '.', label=label2)
    plt.title(features_list[feature])
    plt.legend()
    
def ph(data1, label1, data2, label2, feature, features_list):
    plt.hist(data1[:,feature], 60, label=label1, alpha=0.5)
    plt.hist(data2[:,feature], 60, label=label2, alpha=0.5)
    plt.title(features_list[feature])
    plt.legend()
    
def pp(data1, label1, data2, label2, feature, features_list):
    plt.subplot(211)
    pf(data1, label1, data2, label2, feature, features_list)
    plt.subplot(212)
    ph(data1, label1, data2, label2, feature, features_list)
    plt.savefig(str(feature) + '.png')
    # plt.show()
    
def plot_all():
    for i in np.arange(len(features_list_limited)):
        plt.clf()
        pp(kiwi, 'kiwi', not_kiwi, 'not kiwi', i, features_list_limited)

f = open('features_list.txt', 'r')
features_list = [line.rstrip('\n') for line in f]
f.close()
f = open('features_list_limited.txt', 'r')
features_list_limited = [line.rstrip('\n') for line in f]
f.close()

features_location = '/home/tracek/Ornitokrites/Recordings/'
no_features = 34
X_full = np.empty(shape=(0, no_features))
Y = np.empty(0, 'int')

L = []

for dirpath, dirnames, filenames in os.walk(features_location):
    for filename in filenames:
        if filename.endswith("_data.csv"):
            path = os.path.join(dirpath, filename)
            data = np.loadtxt(path, delimiter=',')
            X_full = np.vstack((X_full, data))
        if filename.endswith("_target.txt"):
            path = os.path.join(dirpath, filename)
            target = np.loadtxt(path, 'int')
            Y = np.hstack((Y, target))

not_kiwi_mask = Y == 0        
kiwi_mask = Y > 0
kiwi_female_mask = Y == 1
kiwi_male_mask = Y == 2

selected_features_idx = []
for f in features_list_limited:
    selected_features_idx.append(features_list.index(f))
    
X_limited = X_full[:,selected_features_idx]
X_scaled = preprocessing.scale(X_limited)

not_kiwi = X_scaled[not_kiwi_mask]
kiwi = X_scaled[kiwi_mask]
kiwi_female = X_scaled[kiwi_female_mask]
kiwi_male = X_scaled[kiwi_male_mask]

X_shape = np.shape(X_scaled)
partition_factor = 10
partition_mask = (np.arange(X_shape[0]) % partition_factor == 0)

test_set = X_scaled[partition_mask]
expected_test_result = Y[partition_mask]
training_set = X_scaled[np.invert(partition_mask)]
training_set_result = Y[np.invert(partition_mask)]

clf = svm.SVC(gamma=0.1, C=2.)
clf.fit(training_set, training_set_result)
prediction = clf.predict(test_set)

result = good_sex = 0
for i in np.arange(len(test_set)):
    if prediction[i] == 0 and expected_test_result[i] == 0:
        result += 1
        good_sex += 1
    elif prediction[i] > 0 and expected_test_result[i] > 0:
        result += 1
        if prediction[i] == expected_test_result[i]:
            good_sex += 1

print 'Kiwi / not kiwi: {}'.format(result * 100 / len(test_set))
print 'Male / Female / not kiwi: {}'.format(good_sex * 100 / len(test_set))
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    