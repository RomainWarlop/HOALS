#!/bin/bash
function run {
	./bdutil --bucket test_spark_romain -z europe-west1-b -n $2 -P spark-std$1-$2 -p data-science-55 -m n1-standard-$1 -e spark_env.sh deploy
	gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-std$1-$2-m --command "sudo apt-get install -y python-virtualenv gfortran libopenblas-dev liblapack-dev build-essential git python-dev python-pip"
	gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-std$1-$2-m --command "git clone https://github.com/RomainWarlop/HOALS.git"
	for line in $(cat /home/romain/Documents/Github/HOALS/google-cloud-deployment/requirements.txt)
	do
		gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-std$1-$2-m --command "sudo pip install $line"
	done
	gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-std$1-$2-m --command "export PYTHONPATH=$PYTHONPATH:/home/romain/Documents/Github/HOALS"
	gcloud --project=data-science-55 compute ssh --zone=europe-west1-b spark-std$1-$2-m --command "pyspark HOALS/bigEcommerce-test.py > resultat.txt"
	exit
}

#run 2 2
#run 2 4
#run 2 8
#run 2 11
#run 4 2
#run 4 4
run 4 5
#run 8 2