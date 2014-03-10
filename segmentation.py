# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 12:55:57 2013

@author: Lukasz Tracewski

Audio segmentation module.
"""

import numpy as np
from aubio import onset


class OnsetDetector(object):
    """ Wrapper class for Aubio onset detector class """

    def __init__(self, detector_type, threshold, window_size):
        """
        Parameters
        ----------
        window_size : int
            FFT size
        detector_type : string
            Available functions are complexdomain, hfc, phase, specdiff,
            energy, specflux, kl and mkl
        threshold : int
            Threshold value for the onset peak picking. Typical values are
            typically within 0.001 and 0.900. Lower threshold values imply
            more onsets detected.

        Returns
        -------
        out : list
            Calculated onsets

        """
        self._window_size = window_size
        self._hop_size = window_size / 2  # number of samples between two runs
        self._threshold = threshold
        self._type = detector_type

    def calculate_onsets(self, sample, sample_rate):
        """
        Calculate onsets of the given signal

        Parameters
        ----------
        sample : 1-d array
            Single-channel audio sample.
        sample_rate : int
            Sample rate in Hz.

        Returns
        -------
        out : list
            Calculated onsets

        """
        # Pad with zeros
        filler = self._hop_size - (len(sample) % self._hop_size)  # number of zeros
        sample = np.pad(sample, (0, filler), 'constant')  # padding

        # Configure onsets' detector
        onset_detector = onset(self._type, self._window_size, self._hop_size, sample_rate)
        onset_detector.set_threshold(self._threshold)

        # Calculate onsets
        onsets = []
        windowed_sample = np.array_split(sample, np.arange(self._hop_size, len(sample), self._hop_size))
        for frame in windowed_sample:
            if onset_detector(frame.astype('float32')):
                onsets.append(onset_detector.get_last())

        # Discard artifact - somehow always onset is detected at zero
        if (len(onsets) > 0 and onsets[0] == 0):
            onsets.pop(0)

        return onsets


class Segmentator(object):
    """
    Class for segmentation of 1-d signal. It uses onset detection methods
    from aubio library to find onsets of a signal. Constructor will create
    segmentator, while calling process will do actual segmentation based on
    provided input.
    """

    def __init__(self, desired_length=0.8, delay=0.2,
                 window_size=2**11, detector_type='energy', threshold=0.01):
        """
        Available methods for detecting onsets are:

        energy
            Energy based distance
            This function calculates the local energy of the input spectral frame.

        hfc
            High-Frequency content
            This method computes the High Frequency Content (HFC) of the input spectral frame.
            The resulting function is efficient at detecting percussive onsets.

        complex
            Complex domain onset detection function
            This function uses information both in frequency and in phase to determine changes in the spectral content
            that might correspond to musical onsets. It is best suited for complex signals such as polyphonic recordings.

        phase
            Phase based onset detection function
            This function uses information both in frequency and in phase to determine changes in the spectral
            content that might correspond to musical onsets. It is best suited for complex signals such as polyphonic recordings.

        specdiff
            Spectral difference onset detection function

        kl
            Kulback-Liebler onset detection function

        mkl
            Modified Kulback-Liebler onset detection function

        specflux
            Spectral flux

        Parameters
        ----------
        desired_length : float
            Length in seconds of the segment
        delay : float
            How much delay in seconds will be taken into account. Total length
            of a segment is a sum of desired_length and delay
        window_size : int
            FFT size
        detector_type : string
            Available functions are complexdomain, hfc, phase, specdiff,
            energy, kl and mkl
        threshold : int
            Threshold value for the onset peak picking. Typical values are
            typically within 0.001 and 0.900. Lower threshold values imply
            more onsets detected.

        Returns
        -------
        out : list
            Calculated onsets

        """
        self._desired_length_s = desired_length
        self._delay_s = delay
        self._onset_detector = OnsetDetector(detector_type, threshold, window_size)

    def process(self, sample, sample_rate):
        """ Perform segmentation on a sample """
        # silence_intervals are arranged as following:
        # (A, (X, Y))
        # A - length of the interval
        # (X, Y) - tuple with start and end of the interval
        self._silence_intervals = []
        # Calculate onsets
        self._onsets = self._onset_detector.calculate_onsets(sample, sample_rate)
        if (self._onsets):
            self._sample = sample
            self._rate = sample_rate

            # Convert length in seconds to length in samples
            desired_length = sample_rate * self._desired_length_s
            delay = sample_rate * self._delay_s

            # Segments with detected signal (non-noise)
            self._sounds = []

            # Perform segmentation
            silence_min = 4 * sample_rate  # Minimal accepted silence length
            for onset, next_onset in zip(self._onsets, self._onsets[1:]):
                distance_next_onset = next_onset - onset
                # Compute silence intervals
                if distance_next_onset > silence_min:
                    start_silence = onset + 2 * sample_rate  # Safety margin
                    end_silence = next_onset - sample_rate   # Safety margin
                    self._silence_intervals.append((end_silence - start_silence, (start_silence, end_silence)))
                # Compute sounds intervals
                start_sound = onset - delay
                if distance_next_onset < desired_length:
                    end_sound = onset + distance_next_onset
                else:
                    end_sound = onset + desired_length
                self._sounds.append((start_sound, end_sound))

            # Add last onset to sounds
            if self._onsets[-1] + desired_length > len(sample):
                self._sounds.append((self._onsets[-1] - delay, len(sample) - 1))
            else:
                self._sounds.append((self._onsets[-1] - delay, self._onsets[-1] + desired_length))

            # Add starting and closing intervals to silence
            silence_min_start = 2 * sample_rate
            silence_min_end = 3 * sample_rate

            distance_to_1st_onset = self._onsets[0]
            if distance_to_1st_onset > silence_min_start:
                start_silence = 0
                end_silence = distance_to_1st_onset - sample_rate
                self._silence_intervals.append((end_silence - start_silence, (start_silence, end_silence)))

            distance_after_last_onset = len(sample) - self._onsets[-1]
            if distance_after_last_onset > silence_min_end:
                start_silence = self._onsets[-1] + 2 * sample_rate
                end_silence = len(sample)
                self._silence_intervals.append((end_silence - start_silence, (start_silence, end_silence)))

            # If there is only one long silence interval, split it into two: otherwise there will
            # be too much averaging
            if len(self._silence_intervals) == 1 and max(self._silence_intervals, key=lambda item: item[0])[0] > 6 * sample_rate:
                item = self._silence_intervals.pop()
                len1 = item[0] / 2
                start1 = item[1][0]
                end1 = start1 + len1
                len2 = item[0] / 2 + 1
                start2 = end1
                end2 = item[1][1]
                self._silence_intervals.append((len1, (start1, end1)))
                self._silence_intervals.append((len2, (start2, end2)))

            if self._silence_intervals:
                self._silence_intervals.sort(key=lambda item: item[0])

    def get_onsets(self):
        """ Return previously computed onsets """
        return self._onsets

    def get_segmented_sounds(self):
        """ Return previously computed sounds (i.e. non-noise signal) """
        return self._sounds

    def get_next_silence(self, sample):
        """ Silence intervals are sorted from longest to shortest
            This function returns next longest silence interval,
            i.e. touple with start and end position, from the dictionary """
        start, end = self._silence_intervals.pop()[1]
        return sample[start:end]

    def get_number_of_silence_intervals(self):
        return len(self._silence_intervals)
