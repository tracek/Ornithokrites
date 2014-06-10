#!/bin/bash

# The following script for installation with APT is provided by courtesy of Neil Ramsay

###################
# Upgrade packages
###################
sudo apt-get update
sudo apt-get upgrade -y

###################
# Install packages
###################
# Development tools
sudo apt-get install git patch build-essential -y

# Python dependencies
sudo apt-get install python-numpy python-matplotlib python-boto python-sklearn python-aubio -y

# Yaafe dependencies
sudo apt-get install cmake cmake-curses-gui libargtable2-0 libargtable2-dev libsndfile1 libsndfile1-dev \
libmpg123-0 libmpg123-dev libfftw3-3 libfftw3-dev liblapack-dev libhdf5-serial-dev libhdf5-7 -y

###################
# Build Yaafe
###################
cd /tmp
wget -O yaafe-v0.64.tgz https://sourceforge.net/projects/yaafe/files/yaafe-v0.64.tgz/download
tar xzf yaafe-v0.64.tgz
cd yaafe-v0.64/

# Patch bug in Yaafe code
patch -l src_cpp/yaafe-core/Ports.h <<EOF
--- src_cpp/yaafe-core/Ports.h  2011-11-07 21:51:10.000000000 +0000
+++ Ports.h     2014-06-09 04:45:22.751597000 +0000
@@ -59,13 +59,13 @@
 template<class T>
 void Ports<T>::add(const T& val)
 {
-       push_back(Port<T>("",val));
+       this->push_back(Port<T>("",val));
 }

 template<class T>
 void Ports<T>::add(const std::string& name, const T& val)
 {
-       push_back(Port<T>(name,val));
+       this->push_back(Port<T>(name,val));
 }

 template<class T>
EOF

mkdir build
cd build
cmake -DWITH_FFTW3=ON -DWITH_HDF5=ON -DWITH_LAPACK=ON -DWITH_MATLAB_MEX=OFF -DWITH_MPG123=ON -DWITH_SNDFILE=ON ../
make
sudo make install
sudo ln -s /usr/local/python_packages/yaafelib /usr/local/lib/python2.7/dist-packages
export YAAFE_PATH=/usr/local/yaafe_extensions/
sudo patch /etc/environment <<EOF
--- /etc/environment    2014-04-16 18:25:15.000000000 +0000
+++ environment 2014-06-09 05:18:44.207597000 +0000
@@ -1 +1,2 @@
 PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"
+YAAFE_PATH="/usr/local/yaafe_extensions"
EOF

###################
# Grab some Kiwis! (10 random)
###################
cd ~
mkdir kiwidata
cd kiwidata
sudo apt-get install xmlstarlet -y
curl http://kiwicalldata.s3.amazonaws.com/ | xmlstarlet fo > index.xml
mkdir -p 5mincounts notkiwi male female additional
for l in `egrep -o '(<Key>)(.*wav)(</Key>)' index.xml | sed 's/<Key>//' | sed 's/<\/Key>//' | sort -R | head -n 10`; do wget -O $l http://kiwicalldata.s3.amazonaws.com/$l ; done

###################
# Download Ornithorkrites
###################
cd ~
git clone https://github.com/tracek/Ornithokrites.git
cd Ornithokrites/
python ornithokrites.py -d ../kiwidata/
