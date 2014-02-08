import matplotlib
matplotlib.use('Agg')
import recordings_io
import noise_reduction as nr
import features

import Tkinter, tkFileDialog
root = Tkinter.Tk()
root.withdraw()
path_recordings = tkFileDialog.askopenfilename()

(rate, sample) = recordings_io.read(path_recordings)
sample = sample.astype('float32')

noise_remover = nr.NoiseRemover()
try:
    out = noise_remover.remove_noise(sample, rate)
except ValueError:
    out = sample
    
segmentator = noise_remover.segmentator
segmented_sounds = segmentator.get_segmented_sounds()

recordings_io.write('out' + '_seg.wav', rate, out, segments=segmented_sounds)



#f = open('feat.out', 'w')
#f2 = open('out.csv','wb')
#header_written = False
#sounds = []
#for start, end in segmentator.get_segmented_sounds():
#    audio = out[start:end]
#    feats = engine.processAudio(np.array([audio]))
#    f.write("\nstart: %i end: %i\n\n" % (start, end))
#    f.write("%s\n\n-------------------\n" % feats)
#    w = csv.DictWriter(f2, feats.keys())
#    if not header_written:    
#        w.writeheader()
#        header_written = True
#    w.writerow(feats)
#    sounds.append(feats)
#    
#f.close()
#f2.close()


#plt.show()
