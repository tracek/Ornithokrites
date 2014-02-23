# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 07:05:19 2014

@author: Lukasz Tracewski
"""

import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn import svm
from sklearn.cross_validation import StratifiedKFold

def load_data(features_location, no_features):
    X = np.empty(shape=(0, no_features))
    Y = np.empty(0, 'int')
    for dirpath, dirnames, filenames in os.walk(features_location):
        for filename in [f for f in filenames if f.endswith(".wav")]:
            data_path = os.path.join(dirpath, filename + '_data.csv')
            data = np.loadtxt(data_path, delimiter=',')
            X = np.vstack((X, data))
            target_path = os.path.join(dirpath, filename + '_target.txt') 
            target = np.loadtxt(target_path, 'int')
            Y = np.hstack((Y, target))
    return X, Y

f = open('features_list.txt', 'r')
features_list = [line.rstrip('\n') for line in f]
f.close()

features_location = '/home/tracek/Ornitokrites/Recordings/'

X, Y = load_data(features_location, len(features_list))
scaler = preprocessing.StandardScaler().fit(X)
X = np.nan_to_num(X)
X = scaler.transform(X)

folds = 5
cv = StratifiedKFold(Y, n_folds=folds)
classifier = svm.SVC(gamma=0.1, C=20., kernel='rbf', tol=0.1, probability=False, random_state=0)

kiwi_correct = 0
gender_correct = 0

for i, (train, test) in enumerate(cv):
    prediction = classifier.fit(X[train], Y[train]).predict(X[test])
    for i in np.arange(len(prediction)):
        if prediction[i] == 0 and Y[test][i] == 0:
            kiwi_correct += 1
            gender_correct += 1
        elif prediction[i] > 0 and Y[test][i] > 0:
            kiwi_correct += 1
            if prediction[i] == Y[test][i]:
                gender_correct += 1
                
print 'StratifiedKFold'
print 'Kiwi / not kiwi: {0:.2f}%'.format(kiwi_correct * 100.0 / len(X))
print 'Overall: {0:.2f}%'.format(gender_correct * 100.0 / len(X))

#pickle.dump(classifier, open('model2.pkl','wb'))
#pickle.dump(scaler, open('scaler2.pkl', 'wb'))













