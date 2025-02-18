#!/bin/bash

# create the cluster
./bdutil --bucket test_spark_romain -z europe-west1-b -n 2 -P spark-cluster -p data-science-55 -m n1-standard-2 -e spark_env.sh deploy
# test_spark_romain : the cluster name
# europe-west1- : location
# 2 : with 2 machines
# data-science-55 : the google cloud project name - PUT YOUR OWN OTHERWISE IT WON'T WORK
# n1-standard-2 : the machine types

# log in to the master
gcloud --project=YOUR_PROJECT_ID compute ssh --zone=europe-west1-b spark-cluster-m
# adapt the above line

# install some needed packets
sudo apt-get install python-virtualenv gfortran libopenblas-dev liblapack-dev build-essential git python-dev python-pip

# download the HOALS repo containing the HOALS main code, a dataset, a test code and the required librairies
git clone https://github.com/RomainWarlop/HOALS.git

cd HOALS

# install python librairies - go grab a coffee !
for line in $(cat google-cloud-deployment/requirements.txt)
do
  sudo pip install $line
done

export PYTHONPATH=$PYTHONPATH:/home/romain/Documents/Github/HOALS

pyspark testHOALS.py
