from pyspark import SparkContext
from parallelHOALS import HOALS

from random import shuffle
import numpy as np
import pandas as pd
import itertools
import time

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

# fix all the random seeds
np.random.seed(0)

path = "/home/romain/Documents/Github/HOALS/"
data = pd.read_csv("3S-70k.csv", sep = ";")

selectedItem = np.unique(data['codssfamille'])
# filter out item which have been seen less than 5 times
itemCount = [np.sum(data['codssfamille']==i) 
    for i in selectedItem]

selectedItem = [selectedItem[i] for i in np.arange(len(selectedItem)) 
                    if itemCount[i]>5]

userId = pd.DataFrame({'fullVisitorId': np.unique(data['fullVisitorId']),
                       'userId': np.arange(len(np.unique(data['fullVisitorId'])))})
                       
catId = pd.DataFrame({'codssfamille': selectedItem,
                       'catId': np.arange(len(selectedItem))})

data2 = pd.merge(pd.merge(data, userId), catId)

numUser = userId.shape[0]
numItem = catId.shape[0]

shuffleUserId = np.arange(numUser)
shuffle(shuffleUserId)
shuffleUserId = list(shuffleUserId)

# weight
data2['nPPview'][data2['nPPview']>50] = 50.0
maxClick = float(np.max(data2['nPPview']))/10

data2['nATC'][data2['nATC']>20] = 20.0
maxATC = float(np.max(data2['nATC']))/10

data2['nConv'][data2['nConv']>10] = 10.0
maxConv = float(np.max(data2['nConv']))/10

# K cross validation
K = 5
KshuffleUserId = []
start = 0
end = int(numUser/K)
L = int(numUser/K)
for k in range(K):
    if k!=(K-1):
        KshuffleUserId.append(shuffleUserId[start:end])
        start = end
        end+=L
    else:
        KshuffleUserId.append(shuffleUserId[start:])

lambdas = [0.01] #[0.01,1.0,10.0]
alphas = [0.01] #[0.01,1.0,10.0]
for k in [0]: #range(K):
    print('*'*20)
    print('start cross-val',k)
    print('*'*20)

    trainUser = []
    testUser = []
    for i in range(K):
        if i==k:
            testUser = KshuffleUserId[i]
        else:
            trainUser.extend(KshuffleUserId[i])

    split = [1 if ((data2['userId'][i] in trainUser) | 
            ((data2['userId'][i] not in trainUser) & (np.random.random()<0.7)))
                else 0 
               for i in range(data2.shape[0])]


    xyrTrain = [(data2['userId'][i],data2['catId'][i],data2['nPPview'][i]/maxClick,
                 data2['nATC'][i]/maxATC,data2['nConv'][i]/maxConv) 
                 for i in range(data2.shape[0])
                 if split[i]==1]

    xyrTest = [(data2['userId'][i],data2['catId'][i],data2['nPPview'][i]/maxClick,
                data2['nATC'][i]/maxATC,data2['nConv'][i]/maxConv) 
                for i in range(data2.shape[0])
                if split[i]==0]
    
    # filling training set
    z_train = list(np.repeat([0,1,2],len(xyrTrain)))
    z_train = list(map(int,z_train))

    xuser_train = [x for (x,y,r1,r2,r3) in xyrTrain] 
    xuser_train = xuser_train + xuser_train + xuser_train # click + atc + conv

    yitem_train = [y for (x,y,r1,r2,r3) in xyrTrain] 
    yitem_train = yitem_train + yitem_train + yitem_train # click + atc + conv

    r_train = [float(r1) for (x,y,r1,r2,r3) in xyrTrain] # click
    r_train.extend([float(r2) for (x,y,r1,r2,r3) in xyrTrain]) # atc
    r_train.extend([float(r3) for (x,y,r1,r2,r3) in xyrTrain]) # conv

    # filling test set
    z_test = list(np.repeat([0,1,2],len(xyrTest)))
    z_test = list(map(int,z_test))

    xuser_test = [x for (x,y,r1,r2,r3) in xyrTest]
    xuser_test = xuser_test + xuser_test + xuser_test # click + atc + conv

    yitem_test = [y for (x,y,r1,r2,r3) in xyrTest] 
    yitem_test = yitem_test + yitem_test + yitem_test # click + atc + conv

    r_test = [float(r1) for (x,y,r1,r2,r3) in xyrTest] # click
    r_test.extend([float(r2) for (x,y,r1,r2,r3) in xyrTest]) # atc
    r_test.extend([float(r3) for (x,y,r1,r2,r3) in xyrTest]) # conv

    inputTrainingSetTensor = pd.DataFrame([xuser_train,yitem_train,z_train,r_train]).T
    inputTestSetTensor = pd.DataFrame([xuser_test,yitem_test,z_test,r_test]).T

    for i in range(3):
        inputTrainingSetTensor[i] = list(map(int,inputTrainingSetTensor[i]))
        inputTestSetTensor[i] = list(map(int,inputTestSetTensor[i]))

    for elt in itertools.product(*[lambdas,alphas]):
        lambda_, alpha = elt
        print('lambda :',lambda_)
        print('alpha :',alpha)

        t0 = time.time()
        C_hat = HOALS(data = inputTrainingSetTensor, dims = [numUser,numItem,3], ranks=[10,200,2], model = 'tucker',
                      lambda_ = lambda_, alpha = alpha, num_iters = 20, implicit = True)
        t1 = time.time()
        print('-'*20)
        print('executation time :',timespend(t1-t0))
        print('-'*20)

        rhat = []
        for i in np.arange(len(r_test)):
            rhat_i = C_hat(z_test[i],xuser_test[i],yitem_test[i])
            rhat.extend([rhat_i])
        rhat = pd.Series(rhat)
        
        numAction = 3
        num = np.zeros(numAction)
        den = np.zeros(numAction)
        for u in range(numUser):
            for a in range(numAction):
                delta = int(len(z_test)/numAction) 
                ind = (np.where(np.array(xuser_test[a*delta:(a+1)*delta])==u)[0]+a*delta).tolist()
                r1 = list(np.array(r_test)[ind])
                r2 = rhat[ind]
                tmp = list(-np.sort(-r2))
                r = [tmp.index(list(r2)[i])/float(len(r1))*r1[i]
                        for i in np.arange(len(r1))]
                r = 100*np.round(sum(r),2)
                num[a]+=r
                den[a]+=np.sum(r1)

        rank = num/den
        print('*'*20)
        print('rank-measure :',rank)
        print('*'*20)