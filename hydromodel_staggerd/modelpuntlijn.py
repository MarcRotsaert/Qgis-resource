#import os
import numpy as np
import pylab as pyl
import plottools as pt
#from waquagrid_toolkit import _handling_axeskwargs #, list_methods
#import waquagrid_toolkit_test as wgtk

def _handling_axeskwargs(kwargs, xveld, yveld):
    if 'axes' not in kwargs:
        ax_handle = pt.SvaAxis.autodetermineplotaxis(xveld, yveld)
        kwargs.update({'axes':ax_handle})
    else: #'axes' in kwargs
        if kwargs['axes'] in [False, None]:
            ax_handle = pt.SvaAxis.autodetermineplotaxis(xveld, yveld)
            kwargs.update({'axes':ax_handle})
        elif isinstance(kwargs['axes'], pyl.Axes):
            pass
        else:
            raise TypeError('kwargs axes: incorrecte waarde')
        #kwargs.update({'axes':ax})
    return kwargs

class _BasisLijnPunt(object):
    def __init__(self):
        self.Lijn = dict()
        self.Punt = dict()
    def _return_geomobj(self):
        if hasattr(self, 'Lijn'):
            geomobj = self.Lijn
        elif hasattr(self, 'Punt'):
            geomobj = self.Punt
        return geomobj

    def _return_xygeomobj(self, obj, xveld, yveld):
        def set_xymethod(self):
            if hasattr(self, 'Lijn'):
                xymethod = 2
            elif hasattr(self, 'Punt'):
                xymethod = 1
            return xymethod
        geomobj = self._return_geomobj()
        xymethod = set_xymethod(self)
        #xlist = [];ylist = []
        #for p, v in selectie.iteritems():#self.Punt.iteritems():
        #naam = v['name']
        if xymethod == 1:
            if 'x' in geomobj[obj]:
                x_o = float(geomobj[obj]['x'])
                y_o = float(geomobj[obj]['y'])
            elif xveld is None:
                x_o = float(geomobj[obj]['n'])
                y_o = float(geomobj[obj]['m'])
            else:
                x_o = xveld[geomobj[obj]['m']-1, geomobj[obj]['n']-1]
                y_o = yveld[geomobj[obj]['m']-1, geomobj[obj]['n']-1]
        elif xymethod == 2:
            if xveld is None:
                x_o = float(geomobj[obj]['L1'][0]+obj['L2'][0])/2
                y_o = float(geomobj[obj]['L1'][1]+obj['L2'][1])/2
            else:
                m_1 = geomobj[obj]['L1'][0]-1
                n_1 = geomobj[obj]['L1'][1]-1
                m_2 = geomobj[obj]['L2'][0]-1
                n_2 = geomobj[obj]['L2'][1]-1
                #print(m1, m2, n1, n2)
                #print(xveld.shape)
                x_o = (xveld[m_1, n_1]+xveld[m_2, n_2])/2
                y_o = (yveld[m_1, n_1]+yveld[m_2, n_2])/2
            #if np.isnan(x) == False:
            #if not np.isnan(x):
            #    xlist.append(x)
            #    ylist.append(y)
                #pyl.text(x, y, naam, *arg, **kwargs)
            #else:
            #    print(str(v) + ' valt buiten grid!!')
        return x_o, y_o

    def return_nummerselect(self, nummerselector):
        """return punten op _Basis van nummers overeenkomend met keys in Punt

        Input:
            nummerselector: lijst puntnummers, iterable integers
        Output:
            geselecteerde punten, list met dictionaries"""
        geomobj = self._return_geomobj()
        selectie = {}
        try:
            iter(nummerselector)
        except TypeError:
            nummerselector = [nummerselector]
        for nrsel in nummerselector:
            try:
                selectie[nrsel] = geomobj[nrsel]
            except KeyError:
                a_str = str(nrsel)+' niet aanwezig. '+u'Wel beschikbaar \n'
                b_str = str(geomobj.keys())
                raise KeyError(a_str+b_str)
        return selectie

    def return_naamselect(self, naamselector, strikt=False):
        """return punten op _Basis van (gedeelte) naam punten
        Input:
            naamselector: string
        Output:
            geselecteerde punten, dictionary"""
        naamselector = naamselector.upper()
        geomobj = self._return_geomobj()
        sel = {}
        #if hasattr(self, 'Lijn'):
        #    geomobj = self.Lijn
        #elif hasattr(self, 'Punt'):
        #    geomobj = self.Punt
        #for p in self.Punt.iterkeys():
        #for obj in geomobj.iterkeys():
        for obj in geomobj:
            if geomobj[obj]['name'] is None:
                continue
            if not strikt:
                #print(naamselector)
                #print(self.Punt[obj]['name'])
                if geomobj[obj]['name'].find(naamselector) > -1:
                    sel[obj] = geomobj[obj]
            elif strikt:
                print(geomobj[obj]['name'])
                print(naamselector)
                if geomobj[obj]['name'].strip() == naamselector.upper().strip():
                    sel[obj] = geomobj[obj]
        if sel == {}:
            #a = 'Niet te selecteren naam: '+naamselector+u'\n'
            #b = 'Beschikbaar zijn: '+ str(self.return_puntlist()[1])
            #raise Exception, 'nog niet geimplementeerd'
            #a= 'Beschikbare locatienamen:'
            error_b = str(self.return_puntlist()[1])
            error_a = 'Niet te selecteren naam: '+naamselector
            raise KeyError(error_b, error_a)
        return sel

    def return_xyboxselect(self, xybox, xveld, yveld):
        """return punten op _Basis van xy-coordinaten

        Input:
            xybox: list met coordinaten. [xmin, xmax, ymin, ymax]
        Output:
            geselecteerde punten, list met dictionaries"""

        geomobj = self._return_geomobj()
        xmin = xybox[0]
        xmax = xybox[1]
        ymin = xybox[2]
        ymax = xybox[3]
        sel = {}
        #assert xmin<xmax & ymin<ymax, str(xmin)+str(xmax)+str(ymin)+str(ymax)
        for obj in geomobj:
            x_o, y_o = self._return_xygeomobj(obj, xveld, yveld)
            if x_o > xmin and x_o < xmax and y_o > ymin and y_o < ymax:
                sel[obj] = geomobj[obj]
        return sel

    def _plot_naam(self, xveld=None, yveld=None, namesel=None, *arg, **kwargs):
        """Plot namen punten naar een kaartje

        Input:
            * xveld, yveld
            * namesel => iterable van strings
            * arg ev => zie matplotlib text\n
            * kwargs => zie matplotlib text
        Output:
            kaartje met punten."""

        kwargs = _handling_axeskwargs(kwargs, xveld, yveld)
        geomobj = self._return_geomobj()
        #xymethod = self.set_xymethod()
        #print(xymethod)
        #if hasattr(self, 'Punt'):
        #    geomobj = self.Punt
        #    xymethod = 1
        #elif hasattr(self, 'Lijn'):
        #    geomobj = self.Lijn
        #    xymethod = 2
        if namesel is not None:
            assert isinstance(namesel, (tuple, list, str))
            if isinstance(namesel, str):
                selectie = self.return_naamselect(namesel, strikt=True)
            else:
                selectie = {}
                for name in namesel:
                    tempsel = self.return_naamselect(name, strikt=True)
                    for temp in tempsel:
                        selectie.update({temp:tempsel[temp]})
        else:
            selectie = geomobj
        xlist = []
        ylist = []
        print(selectie)
        
        for sel_k, sel in selectie.items():#self.Punt.iteritems():
            x_o, y_o = self._return_xygeomobj(sel_k, xveld, yveld)
            naam = sel['name']
            if not np.isnan(x_o):
                xlist.append(x_o)
                ylist.append(y_o)
                pyl.text(x_o, y_o, naam, *arg, **kwargs)
            else:
                print(str(sel) + ' valt buiten grid!!')
        pyl.axis([min(xlist), max(xlist), min(ylist), max(ylist)])
