import recordings_io
import matplotlib.pyplot as plt
import noise_reduction as nr
import segmentation 
import voice_enhancement as ve
import scipy.signal as sig
import pywt
import numpy as np
import yaafelib as yf
import nose.tools as nt

import Tkinter, tkFileDialog
root = Tkinter.Tk()
root.withdraw()
path_recordings = tkFileDialog.askopenfilename()

#path_recordings = '/home/tracek/Ptaszki/Recordings/male/RFPT-LPA-20111128233002-120-60-KR6.wav'
#path_recordings = '/home/tracek/Ptaszki/Recordings/male/RFPT-LPA-20111210220002-120-60-KR6.wav'
#path_recordings = '/home/tracek/Ptaszki/RFPT-LPA-20111128233002-120-60-KR6.wav'


(rate, sample) = recordings_io.read(path_recordings)
sample = sample.astype('float32')
sample_highpassed = nr.highpass_filter(sample, rate, 1500)
segmentator = segmentation.Segmentator()
segmentator.process(sample_highpassed, rate)

silence = segmentator.get_silence()
segmented_sounds = segmentator.get_segmented_sounds()

out = sample

try:
    noise = segmentator.get_next_silence(sample)
    out = ve.reduce_noise(sample, noise, 0)
    noise = segmentator.get_next_silence(sample)
    out = ve.reduce_noise(out, noise, 0)
except KeyError, e:
    print e

out = nr.highpass_filter(out, rate, 1200)

recordings_io.write('out' + '_seg.wav', rate, out, segments=segmented_sounds)

fp = yf.FeaturePlan(sample_rate=rate)
success = fp.loadFeaturePlan('features.config')
nt.assert_true(success, 'features config not loaded correctly')

engine = yf.Engine()
engine.load(fp.getDataFlow())    
engine.reset() 

sounds = []
for start, end in segmentator.get_segmented_sounds():
    audio = out[start:end]
    feats = engine.processAudio(np.array([audio]))
    sounds.append(feats)

plt.specgram(out, NFFT=2**11, Fs=rate)
for start, end in segmented_sounds:
    start /= rate
    end /= rate
    plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2)
    plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
plt.axis('tight')
plt.show()
