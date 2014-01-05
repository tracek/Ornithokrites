Ornitokrites
============
Software for automatic identification of kiwi calls from audio recordings. Pre-alpha, not feature complete.


Usage
==============
ornitokrites.py [bucket name]


What's in:
============
1. Fetching data from provided S3 bucket.
2. Pre-processing, removing low frequencies.
3. Segmentation of audio track into short audio features (non-noise) and silence
   periods (noise).
4. Removal of noise through spectral subtraction. This step produces so-called 
   "musical tones": tin-like sound all over the sample. There is an ongoing effort 
   to make the algorithm smarter. 
5. Saving 'audio features' and spectrograms together with input data.


Current work:
=============
finding best classifiers to identify kiwi.


Future work
=============
Add machine learning algorithm based on found classifiers.


Technology
=============
Python, numerically intensive parts in C/C++.


Deployment
=============
Amazon Web Services, EC2 instance of Ubuntu. In principle it can be installed on 
any operating system, though Unix-like confer least effort. At the end it should act
as a web service that, provided input data, generates a report and sends it to a user.



