# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 20:31:22 2013

@author: Lukasz Tracewski

Various filters
"""

from scipy.signal import firwin, butter, lfilter, kaiserord, wiener
import numpy as np
from segmentation import Segmentator
import noise_subtraction as ns

class NoiseRemover(object):
    
    def remove_noise(self, signal, rate):
        # Apply highpass filter to greatly reduce signal strength below 1500 Hz.  
        self.sample_highpassed = highpass_filter(signal, rate, 1500)
        
        self.segmentator = select_best_segmentator(self.sample_highpassed, rate)
        no_silence_intervals = self.segmentator.get_number_of_silence_intervals()
        
        out = signal

        if no_silence_intervals == 0:
            raise ValueError('Could not find any silence intervals')
        elif no_silence_intervals == 1:
            # Perform spectral subtraction on sample (not high-passed!)
            noise = self.segmentator.get_next_silence(signal) # Get silence period
            out = ns.reduce_noise(signal, noise) # Perform spectral subtraction
        else:
            noise = self.segmentator.get_next_silence(signal) # Get silence period
            out = ns.reduce_noise(signal, noise) # Perform spectral subtraction
            noise = self.segmentator.get_next_silence(signal) # Try again
            out = ns.reduce_noise(out, noise) # Perform spectral subtraction           
        
        # Apply high-pass filter on spectral-subtracted sample
        out = highpass_filter(out, rate, 1500)
        
        return out
   
    
def select_best_segmentator(signal, rate):
    # Segmentator divides a track into segments containing sound features (non-noise)
    # and silence (noise)
    segmentator = Segmentator(detector_type='energy', threshold=0.01)    
    
    # Perform segmentation on high-passed sample
    segmentator.process(signal, rate)
    
    no_silence_intervals = segmentator.get_number_of_silence_intervals()

    if no_silence_intervals < 1:
        segmentator = Segmentator(detector_type='energy', threshold=0.2)
        segmentator.process(signal, rate)
        no_silence_intervals = segmentator.get_number_of_silence_intervals()
    
    return segmentator

def wiener_filter(signal):
    """ Wiener filter. """
    output = wiener(signal, 2**5 - 1)
    return output

def remove_clicks(signal, rate, periodicity):
    """ Clicks are short bursts of energy. """
    energy = calculate_energy(signal, periodicity)
    print energy
    output = signal
    std = np.mean(energy)
    print std
    threshold = 5 * std
    for idx, interval in enumerate(energy):
        if interval > threshold:
            start = idx * periodicity;
            output[start - periodicity:start + 2 * periodicity] = 0
    return output
    
def calculate_energy(signal, period, overlap = 0):
    """ Calculate energy of the signal. """
    intervals = np.arange(0, len(signal), period)
    energy = np.zeros(len(intervals) - 1)
    for i in np.arange(len(intervals) - 1):
        energy_slice = signal[intervals[i]:intervals[i+1]]
        energy[i] = sum(energy_slice**2)
    return energy    

def highpass_filter(signal, rate, cut):
    """ Apply highpass filter. Everything below 'cut' frequency level will
        be greatly reduced. """
    ntaps = 199
    nyq = 0.5 * rate
    highpass = firwin(ntaps, cut, nyq=nyq, pass_zero=False,
                        window='hann', scale=False)
    filteredSignal = lfilter(highpass, 1.0, signal)
    return filteredSignal    

def bandpass_filter(signal, signal_rate, lowcut, highcut, window='hann'):
    """ Apply bandpass filter. Everything below 'lowcut' and above 'highcut' 
        frequency level will be greatly reduced. """    
    ntaps = 199
    nyq = 0.5 * signal_rate
    lowpass = firwin(ntaps, lowcut, nyq=nyq, pass_zero=False,
                     window=window, scale=False)
    highpass = - firwin(ntaps, highcut, nyq=nyq, pass_zero=False,
                        window=window, scale=False)
    highpass[ntaps/2] = highpass[ntaps/2] + 1
    bandpass = -(lowpass + highpass)
    bandpass[ntaps/2] = bandpass[ntaps/2] + 1    
    filteredSignal = lfilter(bandpass, 1.0, signal)
    return filteredSignal

def keiser_bandpass_filter(signal, signal_rate, lowcut, highcut):
    """ Apply bandpass filter. Everything below 'lowcut' and above 'highcut' 
        frequency level will be greatly reduced. Keiser edition. """     
    # The Nyquist rate of the signal.
    nyq_rate = 0.5 * signal_rate
    
    # The desired width of the transition from pass to stop,
    # relative to the Nyquist rate.  We'll design the filter
    # with a 5 Hz transition width.
    width = 5.0 / nyq_rate
    # The desired attenuation in the stop band, in dB.
    ripple_db = 60.0
    # Compute the order and Kaiser parameter for the FIR filter.
    N, beta = kaiserord(ripple_db, width)
    # Use firwin with a Kaiser window to create a lowpass FIR filter.
    lowpass = firwin(N, lowcut / nyq_rate, window=('kaiser', beta))
    highpass = - firwin(N, highcut / nyq_rate, window=('kaiser', beta))
    highpass[N/2] = highpass[N/2] + 1
    bandpass = - (lowpass + highpass)
    bandpass[N/2] = bandpass[N/2] + 1    
    # Use lfilter to filter x with the FIR filter.
    filteredSignal = lfilter(bandpass, 1.0, signal)
    return filteredSignal
        
def _butter_bandpass(lowcut, highcut, fs, order=5):      
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
    
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """ Apply _bandpass filter. Everything below 'lowcut' and above 'highcut' 
        frequency level will be greatly reduced. Butter edition. """       
    b, a = _butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def moving_average(signal, length):
    """ Moving average filter. """
    smoothed = np.convolve(signal, np.ones(length)/length, mode='same')
    return smoothed
