from pyspark import SparkContext
from pyspark.mllib.recommendation import ALS, Rating
from sys import argv

path = "/home/data/file.csv"

data = sc.textFile(path)

data_separator = '\t'

def ALS(data,dim,rank = 5,lambda_=0.8,alpha=0.01,num_iters=20,implicit=False):

	def getRatings(l):
		if float(l[4])==dim:
			return Rating(float(l[0]), float(l[1]), float(l[2]))

	ratings = data.map(lambda l: l.split(data_separator)).map(getRatings)

	if implicit:
		model = ALS.trainImplicit(ratings=ratings, rank=rank, iterations=num_iters, seed=0, lambda_=lambda_, alpha=apha)
	else:
		model = ALS.train(ratings=ratings, rank=rank, iterations=num_iters, seed=0, lambda_=lambda_)

	features = model.userFeatures()
	return features

def HOALS(data,rank = [5,5,5],lambda_=0.8,alpha=0.01,num_iters=20,implicit=False):

	nDim = len(a)
	
