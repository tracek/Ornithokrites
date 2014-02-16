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
    for i in np.arange(len(features_list)):
        plt.clf()
        pp(kiwi_female, 'kiwi_female', kiwi_male, 'kiwi_male', i, features_list)
        
def load_data(features_location):
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
no_features = 11

X, Y = load_data(features_location)
X = np.nan_to_num(X)

not_kiwi_mask = Y == 0        
kiwi_mask = Y > 0
kiwi_female_mask = Y == 1
kiwi_male_mask = Y == 2


X = preprocessing.scale(X)
kiwi = X[kiwi_mask]
kiwi_Y = Y[kiwi_mask]
kiwi_female = X[kiwi_female_mask]
kiwi_male = X[kiwi_male_mask]
not_kiwi = X[not_kiwi_mask]

partition_factor = 5
offset = 3
partition_mask = (np.arange(offset, offset + len(X)) % partition_factor == 0)

test_set = X[partition_mask]
expected_test_result = Y[partition_mask]
training_set = X[np.invert(partition_mask)]
training_set_result = Y[np.invert(partition_mask)]


clf = svm.SVC(gamma=0.1, C=200., kernel='rbf', tol=0.01)
clf.fit(training_set, training_set_result)
prediction = clf.predict(test_set)

kiwi_prediction_mask = prediction != 0
predicted_kiwi = test_set[kiwi_prediction_mask]

kiwi_or_not_kiwi = good_sex = 0
for i in np.arange(len(test_set)):
    if prediction[i] == 0 and expected_test_result[i] == 0:
        kiwi_or_not_kiwi += 1
        good_sex += 1
    elif prediction[i] > 0 and expected_test_result[i] > 0:
        kiwi_or_not_kiwi += 1
        if prediction[i] == expected_test_result[i]:
            good_sex += 1

print 'Kiwi / not kiwi: {0:.2f}%'.format(kiwi_or_not_kiwi * 100.0 / len(test_set))
print 'Male / Female: {0:.2f}%'.format(good_sex * 100.0 / len(test_set))

import pickle
f = open('model.pkl','wb')
pickle.dump(clf, f)
f.close()

from sklearn.cross_validation import StratifiedKFold
folds = 5
cv = StratifiedKFold(Y, n_folds=folds)

classifier = svm.SVC(gamma=0.1, C=10., kernel='rbf', tol=0.001, probability=False, random_state=0)

kiwi_correct = 0
gender_correct = 0
total = 0

for i, (train, test) in enumerate(cv):
    prediction = classifier.fit(X[train], Y[train]).predict(X[test])
    total += len(X[test])
    for i in np.arange(len(prediction)):
        if prediction[i] == 0 and Y[test][i] == 0:
            kiwi_correct += 1
            gender_correct += 1
        elif prediction[i] > 0 and Y[test][i] > 0:
            kiwi_correct += 1
            if prediction[i] == Y[test][i]:
                gender_correct += 1
                
print 'StratifiedKFold'
print 'Kiwi / not kiwi: {0:.2f}%'.format(kiwi_correct * 100.0 / total)
print 'Male / Female: {0:.2f}%'.format(gender_correct * 100.0 / total)








