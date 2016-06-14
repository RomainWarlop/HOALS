from pyspark import SparkContext
from parallelHOALS import HOALS

from random import shuffle
import numpy as np
import pandas as pd
import itertools
import time

sizes = [1,10,100]

def timespend(x):
    if x<60:
        return str(x)+' sec'
    elif x<3600:
        m, s = divmod(x,60)
        m, s = int(m), int(s)
        return str(m)+' min '+str(s)+' sec'
    else:
        m, s = divmod(x,60)
        h, m = divmod(m,60)
        h, m = int(h), int(m)
        return str(h)+' hour '+str(m)+' min '+str(s)+' sec'

for size in sizes:
    # fix all the random seeds
    print("size",size)
    np.random.seed(0)

    path = "/home/romain/Documents/Github/HOALS/"
    for i in range(size):
        if i==0:
            data = pd.read_csv("HOALS/data/bigEcommerce/1.csv")
        else:
            data = pd.concat([data,pd.read_csv("HOALS/data/bigEcommerce/"+str(i+1)+".csv")])

    data['visitorId'] -= 1 # start at 0
    pivotProduct = pd.DataFrame({'productId': list(set(data['productId'])),'itemId': np.arange(len(set(data['productId'])))})
    data = pd.merge(data,pivotProduct)
    del data['productId']

    numUser = len(set(data['visitorId']))
    numItem = len(set(data['itemId']))

    data = pd.melt(data,id_vars=['visitorId','itemId'])
    data = data.rename(columns= {'value' : 'r'})
    data['r'] = list(map(float,data['r']))
    data = data[data['r']>0]
    data.loc[data['variable']=='nView','variable'] = 0
    data.loc[data['variable']=='nClick','variable'] = 1
    data.loc[data['variable']=='nATC','variable'] = 2
    data.loc[data['variable']=='nBuy','variable'] = 3

    data.columns = np.arange(data.shape[1])
    for i in range(3):
        data[i] = list(map(int,data[i]))

    t0 = time.time()
    C_hat = HOALS(data = data, dims = [numUser,numItem,4], ranks=[200,200,2], model = 'tucker',lambda_ = 0.01, alpha = 0.01, num_iters = 20, implicit = True)
    t1 = time.time()
    print('-'*20)
    print('total executation time :',timespend(t1-t0))
    print('-'*20)