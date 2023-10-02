"""_Basisconcept:Toolkit voor bewerkingen met  van Ruimtelijke Waqua elementen

_______________________________________________________________

Datamodel Classes 

niveau 0    ,    niveau 1    ,    niveau 2     ,    niveau 3\n 
_BasisVeldPlot \n
_BasisVeldFunc ,  _BasisVeld     ,   Depveld    ,    Rgfveld\n
.................., .....  .........., Sepveld\n

................., ..............., Uveld=>        Velveld\n

niveau 0    ,    niveau 1    ,    niveau 2     ,    niveau 3 


_Basislijn\n
............., Schotje \n
............., Overlaat\n
             , Ruwheidarea \n

niveau 0\n
_Basislijn=>\n
_BasislijnPunt
                   _BasisLijn_P1P2=>Opening\n
...................                 ., Curve\n
....................                , Barrier\n
                                    , Opening \n
niveau 0\n
_BasislijnPunt
                  Punt

niveau 0\n
Enclosure



niveau 0\n
Dam

___________________________________________________________


Gerelateerde Programma's (niet standaard anaconda):
   - inl_waqua.py
   - plottools.py
   - info_waquaveld.py
   - mask_waquaveld.py
"""
#import os
#import numpy as np
import pylab as pyl
import plottools as pt

from waqua_veld import Depveld, Sepveld, Rgfveld, Uveld, Velveld
from waqua_lijn import Opening, Curve, Overlaat, Barrier, Schotje, Ruwheidarea, Enclosure
from waqua_punt import Dam, Punt
#from modelveld import _BasisVeldFunc, _BasisVeldPlot
#from modellijn import _BasisLijn, _BasisLijn_P1P2
#from modelpuntlijn import _BasisLijnPunt

#import waquagrid_toolkit as wgtk




#from info_waquaveld import veldstatistiek
#veldstatindex = veldstatistiek.index
"""
def list_methods(obj):
    \"""
    return lijst van methodes in object
    \"""
    methods = [method for method in dir(obj) if callable(getattr(obj, method))]
    if methods.count('__init__'):
        methods.remove('__init__')
    return methods

def _handling_axeskwargs(kwargs, xveld, yveld):
    if kwargs.has_key('axes') != True:
        ax = pt.SvaAxis.autodetermineplotaxis(xveld, yveld)
        kwargs.update({'axes':ax})
    else: #kwargs.has_key('axes')
        if kwargs['axes'] in [False, None]:
            ax = pt.SvaAxis.autodetermineplotaxis(xveld, yveld)
            kwargs.update({'axes':ax})
        elif isinstance(kwargs['axes'], pyl.Axes):
            pass
        else:
            raise TypeError, 'kwargs axes: incorrecte waarde'
        #kwargs.update({'axes':ax})
    return kwargs
"""

