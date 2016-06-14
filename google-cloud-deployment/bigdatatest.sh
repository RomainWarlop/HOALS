#!/bin/bash
./bdutil --bucket test_spark_romain -z europe-west1-b -n 4 -P spark-cluster -p data-science-55 -m n1-standard-2 -e spark_env.sh deploy
gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m
sudo apt-get install -y python-virtualenv gfortran libopenblas-dev liblapack-dev build-essential git python-dev python-pip
git clone https://github.com/RomainWarlop/HOALS.git
for line in $(cat HOALS/google-cloud-deployment/requirements.txt)
do
	sudo pip install $line
done
export PYTHONPATH=$PYTHONPATH:/home/romain/Documents/Github/HOALS
pyspark HOALS/bigEcommerce-test.py > resultat.txt
exit
./bdutil --bucket test_spark_romain -z europe-west1-b -n 4 -P spark-cluster -p data-science-55 -m n1-standard-2 -e spark_env.sh delete