#!/bin/bash

# WORK IN PROGRESS !
sudo apt install python-virtualenv gfortran libopenblas-dev liblapack-dev build-essential
rm -rf HOALS
git clone github https://github.com/RomainWarlop/HOALS.git
cd HOALS
virtualenv HOALStest
source HOALStest/bin/activate 
pip install -r google\ cloud\ deployment/requirements.txt
export PYTHONPATH=$PYTHONPATH:/home/romain/Documents/Github/HOALS
pyspark testHOALS.py





