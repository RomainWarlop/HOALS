#!/bin/bash
set -e
function run {
./bdutil --bucket test_spark_romain -z europe-west1-b -n 2 -P spark-cluster -p data-science-55 -m $1 -e spark_env.sh deploy
gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m --command "sudo apt-get install -y python-virtualenv gfortran libopenblas-dev liblapack-dev build-essential git python-dev python-pip"
gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m --command "git clone https://github.com/RomainWarlop/HOALS.git"
for line in $(cat /home/romain/Documents/Github/HOALS/google-cloud-deployment/requirements.txt)
do
gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m --command "sudo pip install $line"
done
gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m --command "export PYTHONPATH=$PYTHONPATH:/home/romain/Documents/Github/HOALS"
gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m --command "source ~/.bashrc && pyspark HOALS/testHOALS.py > resultat$1.txt"
gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m --command "exit"
./bdutil --bucket test_spark_romain -z europe-west1-b -n 2 -P spark-cluster -p data-science-55 -m $1 -e spark_env.sh delete
}

gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m --command "HOALS/testHOALS.py > resultat$1.txt"

machines_type=("n1-standard-2" "n1-standard-4")

for (( i=0; i < ${#machines_type[@]}; i++ )); 
do
echo "start machine type" ${machines_type[i]}
run ${machines_type[i]}
echo "end machine type" ${machines_type[i]}
done