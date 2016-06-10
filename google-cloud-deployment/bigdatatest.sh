#!/bin/bash
function run(){
machine_type=$1
./bdutil --bucket test_spark_romain -z europe-west1-b -n 2 -P spark-cluster -p data-science-55 -m $1 -e spark_env.sh deploy
gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-cluster-m
sudo apt-get install python-virtualenv gfortran libopenblas-dev liblapack-dev build-essential git python-dev
git clone https://github.com/RomainWarlop/HOALS.git
cd HOALS
for line in $(cat google-cloud-deployment/requirements.txt)
do
  sudo pip install $line
done
export PYTHONPATH=$PYTHONPATH:/home/romain/Documents/Github/HOALS
pyspark testHOALS.py > resultat$1.txt
exit
./bdutil --bucket test_spark_romain -z europe-west1-b -n 2 -P spark-cluster -p data-science-55 -m $1 -e spark_env.sh delete
}

machines_type=("n1-standard-2" "n1-standard-4")

for (( i=0; i < ${#machines_type[@]}; i++ )); 
do
echo "start machine type" ${machines_type[i]}
run(${machines_type[i]})
echo "end machine type" ${machines_type[i]}
done