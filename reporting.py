# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 18:05:56 2014

@author: Lukasz Tracewski

Reporting module
"""

import os
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_logger(name, path, stdout=False):
    if not os.path.exists(path):
        os.makedirs(path)
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler=logging.FileHandler(os.path.join(path, name),'w')
    formatter = logging.Formatter('%(message)s <br/>')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('<!DOCTYPE html>')
    if stdout:
        print 'name: %s | path: %s' % (name, path)
        logger.addHandler(logging.StreamHandler()) # for standard output (console)
    else:
        print 'no stdout'
    return logger

def write_results(kiwi_result, individual_calls, filename, audio, rate, segmented_sounds):
    # sample_name_with_dir = filename.replace(os.path.split(os.path.dirname(filename))[0], '')[1:]
    log = logging.getLogger('log.html')                 
    log.info('%s: %s' % (filename.replace('/Recordings',''), kiwi_result))
    
    devlog = logging.getLogger('devlog.html') 
    devlog.info('<h2>%s</h2>' % kiwi_result)
    devlog.info('<h2>%s</h2>' % filename.replace('/Recordings',''))
    devlog.info('<audio controls><source src="%s" type="audio/wav"></audio>', 
                 filename.replace('/var/www/','').replace('/Recordings',''))    
    
    # Plot spectrogram
    plt.ioff()
    plt.specgram(audio, NFFT=2**11, Fs=rate)
    # and mark on it with vertical lines found audio features
    for i, (start, end) in enumerate(segmented_sounds):
        start /= rate
        end /= rate
        plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2, ls='dashed')
        plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
        plt.text(start, 4000, i, fontsize=8)
        if individual_calls[i] == 1:
            plt.plot((start + end) / 2, 3500, 'go')
        elif individual_calls[i] == 2:
            plt.plot((start + end) / 2, 3500, 'bv')
    plt.axis('tight')
    title = plt.title(kiwi_result)
    title.set_y(1.03)
    spectrogram_sample_name = filename + '.png'
    plt.savefig(spectrogram_sample_name)
    plt.clf()
    path = spectrogram_sample_name.replace('/var/www/','').replace('/Recordings','')
    devlog.info('<img src="%s" alt="Spectrogram">', path)
    devlog.info('<hr>')
    
def remove_loggers():
    logging.getLogger('log.html').handlers = []
    logging.getLogger('devlog.html').handlers = []
    logging.shutdown()
    