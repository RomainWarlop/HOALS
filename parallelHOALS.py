from pyspark import SparkContext
from pyspark.mllib.recommendation import ALS#, Rating
from pyspark.sql import SQLContext

sc = SparkContext("local", "HOALS core")
sqlContext = SQLContext(sc)

import pandas as pd
import numpy as np
import sktensor
import re
import itertools

def HOALS(data,dims,ranks,model='tucker',lambda_=0.8,alpha=0.1,num_iters=5,implicit=False):
    """
    Parameters
    data : DataFrame	
        [0] : userId
        [1] : itemId
        [2] : actionId
        [3] : rating
    dims : list
        [0] : number of users
        [1] : number of items
        [2] : number of actions
    """
    C_train = sktensor.sptensor((data[2],data[0],data[1]),
	        data[3],shape=(dims[2],dims[0],dims[1]))

    #==============================================================================
    # recuparation of the (user,item,rate) of the unfold matrix
    #==============================================================================

    # train set
    C1 = sktensor.csr_matrix(C_train.unfold(1))
    y1 = list(C1.indices)
    indptr1 = C1.indptr
    r1 = list(C1.data)
    tmp1 = indptr1[1:len(indptr1)]-indptr1[0:(len(indptr1)-1)]
    x1 = []
    for i in np.arange(len(tmp1)):
        x1.extend(np.repeat(i,tmp1[i]))

    C2 = sktensor.csr_matrix(C_train.unfold(2))
    y2 = list(C2.indices)
    indptr2 = C2.indptr
    r2 = list(C2.data)
    tmp2 = indptr2[1:len(indptr2)]-indptr2[0:(len(indptr2)-1)]
    x2 = []
    for i in np.arange(len(tmp2)):
        x2.extend(np.repeat(i,tmp2[i]))
        
    C3 = sktensor.csr_matrix(C_train.unfold(0))
    y3 = list(C3.indices)
    indptr3 = C3.indptr
    r3 = list(C3.data)
    tmp3 = indptr3[1:len(indptr3)]-indptr3[0:(len(indptr3)-1)]
    x3 = []
    for i in np.arange(len(tmp3)):
        x3.extend(np.repeat(i,tmp3[i]))

    dataTrain = {}
    dataTrain[0] = pd.DataFrame([x1,y1,r1]).T
    dataTrain[1] = pd.DataFrame([x2,y2,r2]).T
    dataTrain[2] = pd.DataFrame([x3,y3,r3]).T
    
    dataTrain[0] = dataTrain[0][dataTrain[0][2]!=0] # where the rating is not null
    dataTrain[1] = dataTrain[1][dataTrain[1][2]!=0]
    dataTrain[2] = dataTrain[2][dataTrain[2][2]!=0]

    #==============================================================================
    # Factorization
    #==============================================================================
    ratings = {}
    res = {}
    features = {}
    for i in range(3):
        if i==0:
            mode = 'User'
        elif i==1:
            mode = 'Item'
        elif i==2:
            mode = 'Action'

        print("Start "+mode+" Learning")
        
        dataTrain[i] = sqlContext.createDataFrame(dataTrain[i]).rdd
        ratings[i] = dataTrain[i].map(lambda l: Rating(float(l[0]), float(l[1]), float(l[2])))
        #ratings[i] = dataTrain[i].map(lambda l: array([float(l[0]), float(l[1]), float(l[2])]))

      # Build the recommendation model using Alternating Least Squares

        if implicit:
            res[i] = ALS.trainImplicit(ratings=ratings[i], rank=ranks[i], iterations=num_iters, seed=0, lambda_=lambda_, alpha=alpha)
        else:
            res[i] = ALS.train(ratings=ratings[i], rank=ranks[i], iterations=num_iters, seed=0, lambda_=lambda_)

        features[i] = res[i].userFeatures()
	
    #==============================================================================
    # Post processing -> export to classic python
    #==============================================================================
    A = {}
    A_star = {}
    for j in range(3):
        features[j] = sqlContext.createDataFrame(features[j]).toPandas()
        A[j] = []
        for i in range(features[j].shape[0]):
            a = features[j].ix[i][1]
            A[j].append(a)
        A[j] = np.array(A[j])
        A_star[j] = np.linalg.pinv(A[j])

    if model=="tucker":
        if implicit:
            tmp = sktensor.sptensor((data[2],data[0],data[1]),list(np.repeat(1,len(data))),
                                        shape=(dims[2],dims[0],dims[1]))
            W = tmp.ttm(A_star[0],mode=1).ttm(A_star[1],mode=2).ttm(A_star[2],mode=0)
        else:
            W = C_train.ttm(A_star[0],mode=1).ttm(A_star[1],mode=2).ttm(A_star[2],mode=0)

        #C_hat = W.ttm(A[0],mode=1).ttm(A[1],mode=2).ttm(A[2],mode=0) # to heavy
        def C_hat(a,u,i):
            out = 0
            P = [range(ranks[i]) for i in range(len(ranks))]
            for elt in itertools.product(*P):
                m,l,s = elt
                out += W[s,m,l]*A[0][u,m]*A[1][i,l]*A[2][a,s]
            
            return out
    elif model=="cp":
        #C_hat = sktensor.ktensor([A[2],A[0],A[1]]).totensor() # to heavy
        def C_hat(a,u,i):
            out = 0
            for r in np.arange(ranks[0]):
                out += A[0][u,r]*A[1][i,r]*A[2][a,r]
            
            return out

    return C_hat