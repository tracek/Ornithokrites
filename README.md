Ornithokrites
============
Ornithokrites is a transliteration of ancient Greek όρνϊθοκρίτης, meaning interpreter of flight or cries of birds. With its rather ambitious name, the program itself is a tool meant for the automatic identification of kiwi calls from audio recordings. It is designed to cope with large variations of environmental conditions and low quality of input data. For each provided audio file, the program tries to find whether it contains any kiwi calls and, if so, whether they are male, female or both.

Usage
==============
There are two ways:

1. **For developer**: ornithokrites.py [*Amazon Web Services bucket name*]. It requires user to install bunch of Python modules, some of which have to be compiled. 
2. **For deployment**: through a web site. User has to provide bucket name and click a button. All calculation are done on Amazon Web Services EC2 instance of Ubuntu. Currently down for upgrade with new release.


What's in:
============
1. Fetching data from provided S3 bucket.
2. Pre-processing, removing low frequencies.
3. Segmentation of audio track into short Regions Of Intrest (ROIs) and silence periods (noise). 
4. Removal of noise through spectral subtraction. This step produces so-called  "musical tones": tin-like sound all over the sample. There is an ongoing effort to make the algorithm smarter, although it does seem to not hurt the program's  performance much - only my ears are bleeding.
5. Calculating following features over ROIs:
   - spectral flatness
   - perceptual spread
   - spectral rolloff
   - spectral decrease
   - spectral shape statistics
   - spectral slope
   - Linear Predictive Coding (LPC)
   - Line Spectral Pairs (LSP)
6. The calculated features are input vectors to Machine Learning algorithm: Support Vector Machines. Individual ROI is marked as kiwi male, kiwi female and not kiwi.


Current work:
=============
Kiwi calls are highly correlated. Make use of this in establishing the result.


Technology
=============
Python, numerically intensive parts in C/C++.


Acknowledgements
=============
I wish to thank Barry Polley for providing this utmost interesting challenge and his assistance along the way. My great appreciation also goes to Pat Miller of [BirdingNZ.net community](http://www.birdingnz.net/) that supplied me with invaluable help concerning kiwi identification; without his aid I would not be able to achieve such high accuracy.


