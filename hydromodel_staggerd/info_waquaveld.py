import numpy as np
from numpy import ma
import gc
import veldstatistiek

def afstandmatrix(X,Y):
    """afstandmatrix van punten
    #invoer: class roostereigenschappen, zie hieronder"""
    assert X.size<15000, "Te veel punten tegelijkertijd ingevoerd.\nVoer een kleiner aantal punten in"        
    from scipy.spatial.distance import pdist,squareform
    Xflat= X.flatten()
    Yflat= Y.flatten()
    #coor= np.array([Xflat ,Yflat]).T
    coor_reshape= np.array([Xflat ,Yflat]).T
    #coor=ma.masked_equal(coor,coor.max())
    #coor_comp=coor.compressed()
    #print(coor_comp.shape)
    #coor_reshape=coor_comp.reshape(coor_comp.size/2,2)
    try:
        afst=pdist(coor_reshape,'euclidean')
    except MemoryError:
        print("Te veel punten tegelijkertijd ingevoerd.\nStart een nieuw terminal scherm of voer een kleiner aantal punten in"        )
        
    else:
        matr=squareform(afst)
        matr=ma.masked_less(matr,1)
        return matr

def flatxy(X,Y):
    #Maak van een veld een 1D- Array
    Yflat= Y.flatten()
    Xflat= X.flatten()
    return Xflat, Yflat


class roostereigenschappen:
    def __init__(self,X,Y):
        assert type(X)==type(np.ma.array([])),"X-veld moet masked array zijn"
        assert type(Y)==type(np.ma.array([])),"Y-veld moet masked array zijn"
        self.X= X
        self.Y=Y
        self.Mmax,self.Nmax=X.shape

    def delta_m(self):
        """afstand rooster in m-richting"""
        delta_m=np.sqrt(np.diff(self.X,axis=0)**2+np.diff(self.Y,axis=0)**2)
        stacktrue=np.ma.array(delta_m.shape[1]*[True],mask=True)
        delta_m=np.ma.vstack([delta_m,stacktrue])
        return delta_m

    def delta_n(self):
        """ afstand rooster in n-richting"""
        delta_n=np.sqrt(np.diff(self.X,axis=1)**2+np.diff(self.Y,axis=1)**2)
        stacktrue=np.ma.array(delta_n.shape[0]*[True],mask=True)
        stacktrue=stacktrue.reshape(stacktrue.shape+(1,))
        delta_n=np.ma.hstack([delta_n,stacktrue])
        return delta_n

    def resolution(self):
        """resolutie"""
        #dm=self.delta_m()[:,0:-1]
        #dn=self.delta_n()[0:-1,:]
        dm=self.delta_m()
        dn=self.delta_n()
        return np.sqrt(dm*dn)

    def orto(self):
        """ orthogonaliteit"""
        mxd= np.diff(self.X,axis=0)[:,0:-1]
        myd= np.diff(self.Y,axis=0)[:,0:-1]
        nxd= np.diff(self.X,axis=1)[0:-1,:]
        nyd= np.diff(self.Y,axis=1)[0:-1,:]
        alfa=np.arctan(nyd/nxd);beta=np.arctan(mxd/myd);
        return np.abs(np.cos(0.5*np.pi+alfa+beta))

    def courant(self,dt,dep):
        """courantgetal
        input:
            dt= tijdstap in secondes (value )
            dep= diepte in meters  ((numpy) array)
        """
        g=9.81
        res=self.resolution()
        print('dt invoer in secondes ('+str(dt)+')')
        #dm=self.delta_m()[:,0:-1]
        #dn=self.delta_n()[0:-1,:]
        return dt*np.sqrt(2*g*dep)/res

    def plot_re(self,parameter,*arg):
        from pylab import pcolormesh
        from mask_staggerdveld import mask_zeta_masker
        attr=dir(self)
        assert(attr.count(parameter)), 'Verkeerde naam voor roostereigenschap opgegeven'  

        #onderstaande is plastisch maar gaat wel werken.
        input=''
        for a in range(len(arg)):
            input=input    +'arg['+str(a)+'],'
        Veldroostereigenschap=eval('self.'+parameter+'('+input+')')
        print(Veldroostereigenschap.shape)
        print(self.X.shape)
        print(self.Y.shape)
        #Plotroostereigenschap=mask_zeta_masker(Veldroostereigenschap,self.X[1:,1:])
        Plotroostereigenschap=mask_zeta_masker(Veldroostereigenschap,self.X)
        pcolormesh(self.X,self.Y,Plotroostereigenschap)

