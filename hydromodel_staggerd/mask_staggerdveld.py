"""Maak een masker voor een waquaveld.
Dit kan verwerkt worden in een figuur in bijvoorbeeld een pcolormesh. 
Voorbeeld pcolormesh(X,Y,Z) 
In pcolormesh worden de coordinaten van de hoekpunten opgegeven voor de cel met de waarde Z.
De array van X en Y is dan ook 1 cel groter in zowel m en n richting als de array van Z 

Voor een staggered grid worden de hoekpunten van een waterstandsveld gevormd door dieptepunten. 
En voor een diepteveld worden de hoekpunten gevormd door waterstandspunten.

Voor plotten geldt: als een van de hoekpunten gemaskert moet worden, dan moet de cel in het midden ook een masker krijgen
Dat is hetgeen in deze module gebeurd.
Voor 
          +   -   +
          |   o   | 
          +   _   + 



mask_zeta_masker: Maak masker voor een Zeta-veld(waterstandspunten) op Basis van een masker van een Diepteveld (Depveld)
mask_zeta_value: Maak masker voor een Zeta-veld op Basis van een waarde in een Diepteveld
mask_dep_masker: Maak masker voor een Diepte-veld op Basis van een masker van een Zetaveld
mask_zeta_value: Maak masker voor een Diepte-veld op Basis van een waarde van een Zetaveld

"""
import numpy.ma as ma
import numpy as np
#from matplotlib.mlab import inside_poly
#from info_waquaveld import veldstatistiek



class plotveld:
    def __init__(self):
        self.Veldtype =    {'dep':{'id':1,'xstack':0,'ystack':0},
                    'zeta':{'id':2,'xstack':1,'ystack':1}}

    def _stack(self,z,veldtype):
        xstack=self.Veldtype[veldtype]['xstack']
        ystack=self.Veldtype[veldtype]['ystack']
        zs=z
        if xstack==1:
            x=np.ma.masked_array(np.zeros([1,z.shape[1]]),mask=True)
            zs=np.ma.vstack([x,z])
        if ystack==1:
            y=np.ma.masked_array(np.zeros([zs.shape[0],1]),mask=True)
            zs=np.ma.hstack([y,zs])
        return zs

    def return_maskmask(self,z,masker,veldtype):
        if type(masker)==ma.MaskedArray:
            masker= masker.mask
        elif masker.dtype!=bool:
            raise TypeError
        try:
            xstack=self.Veldtype[veldtype]['xstack']
            ystack=self.Veldtype[veldtype]['ystack']
        except ValueError:
            print(self.Veldtype.keys())
        print(xstack)
        assert masker.shape[0]==z.shape[0]+1-xstack
        assert masker.shape[1]==z.shape[1]+1-ystack

        m1=masker[0:-1,0:-1] #hoekpunt 1
        m2=masker[1:,1:]     #hoekpunt 2
        m3=masker[1:,0:-1]   #hoekpunt 3
        m4=masker[0:-1,1:]   #hoekpunt 4
        #combineer maskers
        mt= m1|m2|m3|m4
        zm=ma.masked_where(mt,z[xstack:,ystack:])
        zm=self._stack(zm,veldtype)
        """
        if xstack==1:
            x=np.ma.masked_array(np.zeros([1,zm.shape[1]]),mask=True)
            zm=np.ma.vstack([x,zm])
        if ystack==1:
            y=np.ma.masked_array(np.zeros([zm.shape[0],1]),mask=True)
            zm=np.ma.hstack([y,zm])
        """
        return zm

    def return_valuemask(self,z,value,veldtype):
        try:
            maskvalue=float(value)
        except TypeError:
            print('voer waarde in')

        try:
            xstack=self.Veldtype[veldtype]['xstack']
            ystack=self.Veldtype[veldtype]['ystack']
        except KeyError:
            print('Beschikbare invoer voor veldtype: '+self.Veldtype.keys())

        #maak een mask op waterstandlocaties op basis van waarde op dieptepunten
        if xstack==1 and ystack==1:
            zm=z[1:,1:]
        elif xstack==0 and ystack==0:
            zm=z[0:-1,0:-1]
        m1=ma.masked_equal(z[0:-1,0:-1]==value,zm) #hoekpunt 1
        m2=ma.masked_equal(z[1:,1:]==value,zm) #hoekpunt 2
        m3=ma.masked_equal(z[1:,0:-1]==value,zm) #hoekpunt 3
        m4=ma.masked_equal(z[0:-1,1:]==value,zm) #hoekpunt 4
        #combineer maskers
        mt= m1|m2|m3|m4
        #return zm,mt,m1
        zm=ma.masked_where(mt,zm)
        
        zm=self._stack(zm,veldtype)
        #x=np.ma.masked_array(np.zeros([1,zm.shape[1]]),mask=True)
        #zm=np.ma.vstack([zm,x])
        #y=np.ma.masked_array(np.zeros([zm.shape[0],1]),mask=True)
        #zm=np.ma.hstack([zm,y])
        return zm


def mask_zeta_value(z,maskgrid,mask_value):
    #maak een mask op waterstandlocaties op basis van waarde op dieptepunten  
    m1=ma.masked_equal(maskgrid[0:-1,0:-1]==mask_value,z[1:,1:]) #hoekpunt 1
    m2=ma.masked_equal(maskgrid[1:,1:]==mask_value,z[1:,1:]) #hoekpunt 2
    m3=ma.masked_equal(maskgrid[1:,0:-1]==mask_value,z[1:,1:]) #hoekpunt 3
    m4=ma.masked_equal(maskgrid[0:-1,1:]==mask_value,z[1:,1:]) #hoekpunt 4
    #combineer maskers
    mt= m1.mask|m2.mask|m3.mask|m4.mask
    zm=ma.masked_where(mt,z[1:,1:])
    
    x=np.ma.masked_array(np.zeros([1,zm.shape[1]]),mask=True)
    zm=np.ma.vstack([zm,x])
    y=np.ma.masked_array(np.zeros([zm.shape[0],1]),mask=True)
    zm=np.ma.hstack([zm,y])
    return zm

def mask_dep_value(z,maskgrid,mask_value):
    #maak een mask voor dieptepunt locaties op basis van zmerstandpunten 
    
    m1=ma.masked_equal(maskgrid[1:,1:]==mask_value,z[0:-1,0:-1]) #hoekpunt 1
    m2=ma.masked_equal(maskgrid[0:-1,0:-1]==mask_value,z[0:-1,0:-1]) #hoekpunt 2
    m3=ma.masked_equal(maskgrid[1:,0:-1]==mask_value,z[0:-1,0:-1]) #hoekpunt 3
    m4=ma.masked_equal(maskgrid[0:-1,1:]==mask_value,z[0:-1,0:-1]) #hoekpunt 4
    #combineer maskers
    mt= m1.mask|m2.mask|m3.mask|m4.mask
    zm=ma.masked_where(mt,z[0:-1,0:-1])
    
    x=np.ma.masked_array(np.zeros([1,zm.shape[1]]),mask=True)
    zm=np.ma.vstack([zm,x])
    y=np.ma.masked_array(np.zeros([zm.shape[0],1]),mask=True)
    zm=np.ma.hstack([zm,y])
    #print(zm.shape)
    return zm


def mask_zeta_masker(z,masker):
    zshape=str(z.shape);
    maskershape=str(masker.shape)
    assert(masker.shape==z.shape),"afmetingen arrays moeten het zelfde zijn: maskershape ="+maskershape+"zshape="+zshape
    if type(masker)==ma.MaskedArray:
        masker= masker.mask
    elif masker.dtype!=bool:
        raise TypeError
    z=z[1:,1:]

    m1=masker[0:-1,0:-1] #hoekpunt 1
    m2=masker[1:,1:] #hoekpunt 2
    m3=masker[1:,0:-1] #hoekpunt 3
    m4=masker[0:-1,1:]#hoekpunt 4
    #combineer maskers
    mt= m1|m2|m3|m4
    #zm=ma.masked_where(mt,z[1:,1:])
    zm=ma.masked_where(mt,z)

    x=np.ma.masked_array(np.zeros([1,zm.shape[1]]),mask=True)
    zm=np.ma.vstack([x,zm])
    y=np.ma.masked_array(np.zeros([zm.shape[0],1]),mask=True)
    zm=np.ma.hstack([y,zm])
    return zm

def mask_dep_masker(z,masker):
    assert(masker.shape[0]==z.shape[0]+1 and masker.shape[1]==z.shape[1]+1 ),"masker moeten 1 groter zijn dan dieptepuntenveld"
    if type(masker)==ma.MaskedArray:
        masker= masker.mask
    elif masker.dtype!=bool:
        raise TypeError
    #maak een mask voor dieptepunt locaties op basis van masker op waterstandpunten 
    m1=masker[1:,1:]#hoekpunt 1
    m2=masker[0:-1,0:-1] #hoekpunt 2
    m3=masker[1:,0:-1] #hoekpunt 3
    m4=masker[0:-1,1:] #hoekpunt 4
    #combineer maskers
    mt= m1|m2|m3|m4

    zm=ma.masked_where(mt,z)
    return zm


def mask_containspoints(X,Y,path, maskinout='in'):
    coor=ma.masked_array([X.flatten(),Y.flatten()]).T
    inpoly=path.contains_points(coor)
    if maskinout=='out':
        inpoly=~inpoly
    maskout=inpoly.reshape(X.shape)
    return maskout