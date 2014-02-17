Ornithokrites
============
Software for automatic identification of kiwi calls from audio recordings. Pre-alpha, feature complete. What's left is tuning the machine learing algorithm.


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


