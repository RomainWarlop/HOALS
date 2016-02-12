import numpy as np
import scipy.sparse as sparse
from scipy.sparse.linalg import spsolve
import sktensor

class HOALS(object):
    
    def __init__(self,C,kU,kI,kA,penalty=0.8,max_iter=30):
#==============================================================================
# C is construct as a sparse tensor as follow 
# C = sktensor.sptensor((z,x,y),r,shape=(numAction,numUser,numItem))
# kU (resp. kI and kA) is the number of user (resp. item and action) latent variable
#==============================================================================
        self.C = C
        self.kU = kU
        self.kI = kI
        self.kA = kA
        self.penalty = penalty
        self.max_iter = max_iter
        self.num_users = C.shape[1]
        self.num_items = C.shape[2]
        self.num_actions= C.shape[0]
        self.dim = (self.num_users,self.num_items,self.num_actions)
        self.C1 = sktensor.csr_matrix(self.C.unfold(1))
        self.C2 = sktensor.csr_matrix(self.C.unfold(2))
        self.C3 = sktensor.csr_matrix(self.C.unfold(0))
        self.user_vectors = np.random.normal(size=(self.num_users,self.kU))
        self.V1 = np.random.normal(size=(self.num_items*self.num_actions,self.kU))
        self.item_vectors = np.random.normal(size=(self.num_items,self.kI))
        self.V2 = np.random.normal(size=(self.num_users*self.num_actions,self.kI))
        self.action_vectors = np.random.normal(size=(self.num_actions,self.kA))
        self.V3 = np.random.normal(size=(self.num_items*self.num_users,self.kA))


    def trainImplicit(self):
        
        for mode in range(3):
            
            if mode==0:
                for i in xrange(self.max_iter):
                    self.user_vectors = self.iterationImplicit(mode,True, sparse.csr_matrix(self.V1))
                    self.V1 = self.iterationImplicit(mode,False, sparse.csr_matrix(self.user_vectors))
            
            elif mode==1:
                for i in xrange(self.max_iter):
                    self.item_vectors = self.iterationImplicit(mode,True, sparse.csr_matrix(self.V2))
                    self.V2 = self.iterationImplicit(mode,False, sparse.csr_matrix(self.item_vectors))
            
            elif mode==2:
                for i in xrange(self.max_iter):
                    self.action_vectors = self.iterationImplicit(mode,True, sparse.csr_matrix(self.V3))
                    self.V3 = self.iterationImplicit(mode,False, sparse.csr_matrix(self.action_vectors))

        # once finished, we compute the core tensor
        self.getCoreTensor()

    def train(self):
        
        for mode in range(3):
            
            if mode==0:
                for i in xrange(self.max_iter):
                    self.user_vectors = self.iteration(mode,True, sparse.csr_matrix(self.V1))
                    self.V1 = self.iterationImplicit(mode,False, sparse.csr_matrix(self.user_vectors))
            
            elif mode==1:
                for i in xrange(self.max_iter):
                    self.item_vectors = self.iteration(mode,True, sparse.csr_matrix(self.V2))
                    self.V2 = self.iterationImplicit(mode,False, sparse.csr_matrix(self.item_vectors))
            
            elif mode==2:
                for i in xrange(self.max_iter):
                    self.action_vectors = self.iteration(mode,True, sparse.csr_matrix(self.V3))
                    self.V3 = self.iterationImplicit(mode,False, sparse.csr_matrix(self.action_vectors))

        
        # once finished, we compute the core tensor
        self.getCoreTensor()

    def iteration(self, user, fixed_vecs):
        if mode==0:
            num_solve = self.num_users if user else self.num_items*self.num_actions
            lambda_eye = self.penalty * sparse.eye(self.kU)
            solve_vecs = np.zeros((num_solve, self.kU))
        elif mode==1:  
            num_solve = self.num_items if user else self.num_users*self.num_actions
            lambda_eye = self.penalty * sparse.eye(self.kI)
            solve_vecs = np.zeros((num_solve, self.kI))
        elif mode==2:
            num_solve = self.num_actions if user else self.num_users*self.num_items
            lambda_eye = self.penalty * sparse.eye(self.kA)
            solve_vecs = np.zeros((num_solve, self.kA))
        YTY = fixed_vecs.T.dot(fixed_vecs)
        lambda_eye = self.penalty * sparse.eye(self.num_factors)
        solve_vecs = np.zeros((num_solve, self.num_factors))

        for i in xrange(num_solve):
            if user:
                if mode==0:
                    counts_i = self.C1[i].toarray()
                elif mode==1:
                    counts_i = self.C2[i].toarray()
                elif mode==2:
                    counts_i = self.C3[i].toarray()
            else:
                if mode==0:
                    counts_i = self.C1[:, i].T.toarray()
                elif mode==1:
                    counts_i = self.C2[:, i].T.toarray()
                elif mode==2:
                    counts_i = self.C3[:, i].T.toarray()
            YTR = fixed_vecs.T.dot(C_i.T)
            xu = spsolve(YTY + (C_i!=0).sum()*lambda_eye, YTR)
            solve_vecs[i] = xu

    def iterationImplicit(self, mode, user, fixed_vecs):
        if mode==0:
            num_solve = self.num_users if user else self.num_items*self.num_actions
            lambda_eye = self.penalty * sparse.eye(self.kU)
            solve_vecs = np.zeros((num_solve, self.kU))
        elif mode==1:  
            num_solve = self.num_items if user else self.num_users*self.num_actions
            lambda_eye = self.penalty * sparse.eye(self.kI)
            solve_vecs = np.zeros((num_solve, self.kI))
        elif mode==2:
            num_solve = self.num_actions if user else self.num_users*self.num_items
            lambda_eye = self.penalty * sparse.eye(self.kA)
            solve_vecs = np.zeros((num_solve, self.kA))
        num_fixed = fixed_vecs.shape[0]
        YTY = fixed_vecs.T.dot(fixed_vecs)
        eye = sparse.eye(num_fixed)


        for i in xrange(num_solve):
            if user:
                if mode==0:
                    counts_i = self.C1[i].toarray()
                elif mode==1:
                    counts_i = self.C2[i].toarray()
                elif mode==2:
                    counts_i = self.C3[i].toarray()
            else:
                if mode==0:
                    counts_i = self.C1[:, i].T.toarray()
                elif mode==1:
                    counts_i = self.C2[:, i].T.toarray()
                elif mode==2:
                    counts_i = self.C3[:, i].T.toarray()
            CuI = sparse.diags(counts_i, [0])
            pu = counts_i.copy()
            pu[np.where(pu != 0)] = 1.0
            YTCuIY = fixed_vecs.T.dot(CuI).dot(fixed_vecs)
            YTCupu = fixed_vecs.T.dot(CuI + eye).dot(sparse.csr_matrix(pu).T)
            xu = spsolve(YTY + YTCuIY + lambda_eye, YTCupu)
            solve_vecs[i] = xu


        return solve_vecs

    def getCoreTensor(self,orthonormal=True):
#==============================================================================
#         self.W = np.zeros([self.kA,self.kU,self.kI])
#         for ka in np.arange(self.kA):
#             for a in np.arange(self.num_actions):
#                 self.W[ka,:,:] += self.action_vectors[a,ka]*(
#                                 self.user_vectors.T.dot(
#                                 self.C[a,:,:].dot(self.item_vectors)))
#==============================================================================
        if orthonormal:
            self.W = self.C.ttm(self.user_vectors.T,mode=1).ttm(
                                self.item_vectors.T,mode=2).ttm(
                                self.action_vectors.T,mode=0)
        else:
            U1 = np.linalg.pinv(self.user_vectors)
            I1 = np.linalg.pinv(self.item_vectors)
            A1 = np.linalg.pinv(self.action_vectors)
            self.W = self.C.ttm(U1,mode=1).ttm(I1,mode=2).ttm(A1,mode=0)

    def predict(self):
        C_hat = self.W.ttm(self.user_vectors,mode=1).ttm(
                            self.item_vectors,mode=2).ttm(
                            self.action_vectors,mode=0)
        return C_hat