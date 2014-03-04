Ornithokrites
============
Ornithokrites is a transliteration of ancient Greek όρνϊθοκρίτης, meaning interpreter of flight or cries of birds. With its rather ambitious name, the program itself is a tool meant for an automatic identification of kiwi calls from low quality audio recordings. It has been designed to cope with large variations of environmental conditions and low quality of input data. For each provided audio file, the program enables detection of any kiwi calls and, in case they are present, which gender they belong to (male, female or both).

Features
=============
- **Reliable**: stratified 5-fold cross-validation on 206 samples gives the program 97% accuracy.
- **Easy to use**: no installation needed. User can log-in to a web site, provide Amazon Web Services bucket name and execute the program with one click. If in doubt a detailed report is available, containing spectrogram with marked kiwi calls and option to play the audio file in question. This way it should be easy to verify correctness of results. The program resides on Amazon EC2 instance, so getting data from S3 buckets is fast. When things go awry (and they will) I can directly debug and fix issues on the server.
- **Fast**: Sort of. The application spawns separate processes for getting recordings, writing results and calculations. Calculations are done on one or more processes, typically equal to number of cores. On my Core-i5 @3.40GHz it takes 1m40s to process 206 files.

Usage
==============
Expected input are monaural (single-channel) audio files in Waveform Audio File Format (commonly known as WAV or WAVE). The following sections explain two ways of running the program: user-friendly (Web Interface) and user-hostile (install-yourself).

Web interface
--------------
If the data is stored on Amazon Web Services S3 bucket, then by far the easiest way of using the program is through a password-protected web site. This protection is necessary since only one user at a time can run the program. After providing the credentials, the user is directed to a simple web form that serves as an interface to the application. The form contains the following:

- Bucket name: name of Amazon Web Services S3 bucket.
- Execute: connect to data store, download the recordings and run kiwi calls identification. It is a long-lasting operation. Closing the web page does not stop the program.
- Report: show results. Since they are generated live, user can click the button at any moment to get current state of affairs. Only text is printed, making it very fast.
- Show details: show detailed results. In this mode additional data is provided: spectrogram with identified Regions Of Interest: blue triangles are detected male kiwi calls and green circles stand for female kiwi calls. Please keep in mind that a single detected kiwi call does not make a kiwi; only calls that appear in clusters are considered as candidates. Additionally, an option to play the original audio is provided, allowing the user to verify program's predictions.
- Clear: stop execution of the program and clear all intermediate results.

Interactive mode
-----------------
The program is written in Python, which means that running it directly (either from command line or in interactive mode) requires installation of all dependent modules. Due to the dependencies between modules, their installation may prove difficult.

### Batch mode - command line
Executing program with '-h' switch, i.e. ornithiokrites.py -h, will print the complete help with command line arguments explained. This mode allows batch processing of files stored on a disc.

### Single-file mode - graphical user interface
If no command line arguments are provided then program will start in interactive mode. With open file dialogue user can select a single file for analysis.

How it works
============
After the recordings are ready following steps take place:

1. **Apply high-pass filter**. This step will reduce strength of any signal below 1500 Hz. Previous experiments have demonstrated that kiwi rarely show any vocalization below this value. It also helps to eliminate bird calls which are of no interest to the user, e.g. morepork.
2. **Find Regions of Interest** (ROIs), defined as any signal different than background noise. Since length of a single kiwi call is roughly constant, ROI length is fixed to one second. First onsets are found by calculating local energy of the input spectral frame and taking those above certain dynamically-assessed threshold. Then from the detected onset a delay of -0.2s is taken to compensate for possible discontinuities. End of ROI is defined as +0.8s after beginning of the onset, summing to 1s interval. The algorithm is made sensitive, since the potential cost of not including kiwi candidate in a set of ROIs is much higher then adding noise-only ROI.
3. **Reduce noise**. Since ROIs are identified, Noise-Only Regions (NORs) can be estimated as anything outside ROIs (including some margin). Based on NORs spectral subtraction is performed: knowing noise spectrum we can try to eliminate noise over whole sample.
4. **Calculate Audio Features** Those features will serve as a kiwi audio signature, allowing to discriminate kiwi male from female - and a kiwi from any other animals. Audio Features are calculated with Yaafe library. On its [project page](http://yaafe.sourceforge.net/features.html) a complete description of above-mentioned features can be found. For each ROI following features are calculated:
   - spectral flatness
   - perceptual spread
   - spectral rolloff
   - spectral decrease
   - spectral shape statistics
   - spectral slope
   - Linear Predictive Coding (LPC)
   - Line Spectral Pairs (LSP)
5. **Perform kiwi identification**. At this stage Audio Features are extracted from the recording. Based on these, a Machine Learning algorithm, that is Support Vector Machine (SVM), will try to classify ROI as kiwi male, kiwi female and not a kiwi. Additional rules are then applied, employing our knowledge on repetitive character of kiwi calls. Only in case a sufficiently long set of calls is identified, the kiwi presence is marked. 
6. **Report**. Algorithm output can be: female, male, male and female and no kiwi detected.


Dependencies
=============
Following libraries are used by Ornithokrites:
- [Aubio 4.0](http://aubio.org/) - a great tool designed for the extraction of annotations from audio signals.
- [Yaafe 0.64](http://yaafe.sourceforge.net/) - an audio features extraction toolbox with load of features to choose from.
- [scikit-learn](http://scikit-learn.org/) - powerful Machine Learning library.
- [NumPy](http://www.numpy.org/), [SciPy](http://www.scipy.org/) - canonical Python numerical libraries.
- [matplotlib](http://matplotlib.org/) - plotting spectrograms.
- [boto](https://github.com/boto/boto) - connection with Amazon Web Services.

Acknowledgements
=============
I wish to thank Barry Polley for providing this utmost interesting challenge and his assistance along the way. My great appreciation also goes to Pat Miller of [BirdingNZ.net community](http://www.birdingnz.net/) that supplied me with invaluable help concerning kiwi identification; without his aid I would not be able to achieve such high accuracy.


