from pyspark import SparkContext
from pyspark.mllib.recommendation import ALS, Rating
from sys import argv

path = '/home/romain/Data/Input/ml-100k/u.data'

#sc = SparkContext("local", "Simple App")

def getRatings(p):
	return data.map(lambda l: l.split('\t')).map(lambda l: Rating(float(l[0]), float(l[1]), float(l[2])))

data = sc.textFile(path)

ratings = getRatings(1)
bob = ALS.trainImplicit(ratings=ratings, rank=5, iterations=5)


