1#import os
import numpy as np
import pylab as pyl
import plottools as pt

from modelpuntlijn import _BasisLijnPunt
#from waquagrid_toolkit import _handling_axeskwargs # list_methods
#import waquagrid_toolkit as wgtk

def _handling_axeskwargs(kwargs, xveld, yveld):
    if 'axes' not in kwargs:
        ax_handle = pt.SvaAxis.autodetermineplotaxis(xveld, yveld)
        kwargs.update({'axes':ax_handle})
    else: #kwargs.has_key('axes')
        if kwargs['axes'] in [False, None]:
            ax_handle = pt.SvaAxis.autodetermineplotaxis(xveld, yveld)
            kwargs.update({'axes':ax_handle})
        elif isinstance(kwargs['axes'], pyl.Axes):
            pass
        else:
            raise TypeError('kwargs axes: incorrecte waarde')
        #kwargs.update({'axes':ax})
    return kwargs


class _BasisLijn(object):
    """_Basis class voor lijnelementen.
        Lijnelementen bestaan uit volgende attributen:
            (self.)Lijn
    """
    #uvtype = tabel voor begin- en eindpunt in m, n coordinaten
    uvtype = {1:[[0, -1], [0, 0]], #u1, overlaat, schot, opening ruwheid
              2:[[-1, 0], [0, 0]], #v2, overlaat, schot, opening, ruwheid
              3:[[1, -1], [0, -1]],  #v3, overlaat
              4:[[0, -1], [-1, -1]], #v4, overlaat
              5:[[0, 0], [-1, 0]],   #v5, overlaat
              6:[[1, 0], [0, 0]]}    #v6, overlaat

    def __init__(self):
        self.Lijn = dict()

    def __getitem__(self, key):
        """
        Slicing laten werken op attribuurt Lijn.
        """
        return self.Lijn[key]

    def _check_lijn(self):
        #try:
        if isinstance(self.Lijn, list):
            for lijn in self.Lijn:
                assert 'utype' in lijn
                assert 'vtype' in lijn
        elif isinstance(self.Lijn, dict):
            for lijn in self.Lijn:
                
                assert 'utype' in self.Lijn[lijn]
                assert 'vtype' in self.Lijn[lijn]
        #except KeyError, Argument:
        #    print('ontbrekende key in dictionary', Argument)
        #except AttributeError, Argument:
        #    print('geen Lijn dictionary?', Argument)

    def return_xy(self, xveld=None, yveld=None):
        """
        uvtype= {1:[[0, -1], [0, 0]], #u1, overlaat, schot, opening ruwheid
            2:[[-1, 0], [0, 0]], #v2, overlaat, schot, opening, ruwheid
            3:[[1, -1], [0, -1]],  #v3, overlaat
            4:[[0, -1], [-1, -1]], #v4, overlaat
            5:[[0, 0], [-1, 0]],   #v5, overlaat
            6:[[1, 0], [0, 0]]}    #v6, overlaat

        Input:
            xveld, yveld [array of NONE]
        Output:
            List met array bestaande uit coordinaten beginpunt en eindpunt
        """
        self._check_lijn()
        if xveld is not None:
            assert yveld is not None
        xyreturn = []
        #x_a = float;y_a = float;x_b = float;y_b = float
        if isinstance(self.Lijn, dict):
            lijnenatr = self.Lijn.values()
        else:
            lijnenatr = self.Lijn

        #Alle Lijnelementen
        for l_elem in lijnenatr:
            m_1 = l_elem['L1'][0]
            n_1 = l_elem['L1'][1]
            lelem_dmn = []
            if l_elem['utype'] == 0 and l_elem['vtype'] > 2:
                continue
            if l_elem['vtype'] != 0:
                lelem_dmn.append(self.uvtype[l_elem['vtype']])
            if l_elem['utype'] != 0:
                lelem_dmn.append(self.uvtype[1])
            if l_elem['utype'] > 1:
                lelem_dmn.append(self.uvtype[l_elem['utype']])

            lijnxy = []
            for l_dmn in lelem_dmn:
                if xveld is None:
                    x_a = int
                    y_a = int
                    x_b = int
                    y_b = int

                    x_a = m_1+l_dmn[0][0]
                    y_a = n_1+l_dmn[0][1]
                    x_b = m_1+l_dmn[1][0]
                    y_b = n_1+l_dmn[1][1]
                else:
                    x_a = float
                    y_a = float
                    x_b = float
                    y_b = float

                    x_a = xveld[m_1-1+l_dmn[0][0], n_1-1+l_dmn[0][1]]
                    y_a = yveld[m_1-1+l_dmn[0][0], n_1-1+l_dmn[0][1]]
                    x_b = xveld[m_1-1+l_dmn[1][0], n_1-1+l_dmn[1][1]]
                    y_b = yveld[m_1-1+l_dmn[1][0], n_1-1+l_dmn[1][1]]
                lijnxy.append([x_a, y_a])
                lijnxy.append([x_b, y_b])

            if 'L2' in l_elem:
                if l_elem['L1'] != l_elem['L2']: #bijvoorbeeld schot
                    if l_elem['utype'] == 1:
                        m_1 = l_elem['L1'][0]
                        n_s = np.min([l_elem['L1'][1], l_elem['L2'][1]])
                        n_e = np.max([l_elem['L1'][1], l_elem['L2'][1]])
                        for n_t in range(n_s-1, n_e+1):
                            if xveld is None:
                                x_a = m_1
                                y_a = n_t
                            else:
                                x_a = xveld[m_1-1, n_t-1]
                                y_a = yveld[m_1-1, n_t-1]
                            lijnxy.append([x_a, y_a])

                    elif l_elem['vtype'] == 2:
                        n_1 = l_elem['L1'][1]
                        m_s = np.min([l_elem['L1'][0], l_elem['L2'][0]])
                        m_e = np.max([l_elem['L1'][0], l_elem['L2'][0]])
                        #mrange = range(l_elem['L1'][0]+1, l_elem['L2'][0]+1)
                        for m_t in range(m_s-1, m_e+1):
                            if xveld is None:
                                x_a = m_t
                                y_a = n_1
                            else:
                                x_a = xveld[m_t-1, n_1-1]
                                y_a = yveld[m_t-1, n_1-1]
                            lijnxy.append([x_a, y_a])
                else:#l_elem['L1'] == l_elem['L2']
                    m_1 = l_elem['L1'][0]
                    n_1 = l_elem['L1'][1]
                    if l_elem['utype'] == 1:
                        if xveld is None:
                            x_a = m_1
                            y_a = n_1-1
                            x_b = m_1
                            y_b = n_1
                        else:
                            x_a = xveld[m_1-1, n_1-2]
                            y_a = yveld[m_1-1, n_1-2]
                            x_b = xveld[m_1-1, n_1-1]
                            y_b = yveld[m_1-1, n_1-1]
                        lijnxy = [[x_a, y_a], [x_b, y_b]]
                    elif l_elem['vtype'] == 2:
                        if xveld is None:
                            x_a = m_1-1
                            y_a = n_1
                            x_b = m_1
                            y_b = n_1
                        else:
                            x_a = xveld[m_1-2, n_1-1]
                            y_a = yveld[m_1-2, n_1-1]
                            x_b = xveld[m_1-1, n_1-1]
                            y_b = yveld[m_1-1, n_1-1]
            xyreturn.append(np.array(lijnxy))
        return xyreturn

    def _return_mn2lijnindex(self, m_in, n_in):
        """
        Input:
            m, m-coordinaat, n: n-coordinaat [int]
        Output:
            Index nummer in self.Lijn voor (beginpunt) lijnelement
        """
        for ind in range(len(self.Lijn)):
            if self.Lijn[ind]['L1'] == [m_in, n_in]:
                return ind
        print('niet aanwezig')
        return None

    def plot_lijn(self, xveld=None, yveld=None, *args, **kwargs):
        """ plot lijnelemente in kaartje
        Input:
            - xveld = x-coordinaten, [None of array overeenkomend modelveld]
            - yveld = y-coordinaten, [None of array overeenkomend modelveld]
            - *args en **kwargs: zie matplotlib.plot
        """

        kwargs = _handling_axeskwargs(kwargs, xveld, yveld)
        print(kwargs)
        lhandles = []
        if len(self.Lijn) > 10000 and xveld is not None:
            print('Je probeert heel veel lijnen te plotten in xy coordinaten.')
            print('Dit kan zeer lang duren.')
            print('Overweeg om de lijnstukken in mn-coordinaten te plotten')
            pyl.pause(2)

        xylijn = self.return_xy(xveld, yveld)
        dtime = [0, 10, 25, 50, 75, 100, 101]
        count = 0
        print('plot lijn:')
        for xyplot in xylijn:
            try:
                lobj = pyl.plot(xyplot[:, 0], xyplot[:, 1], *args, **kwargs)
            except:
                print('Fail in:'+self+'->'+str(xyplot))
            lhandles.append(lobj[0])

            if (float(count)/len(xylijn))*100. > dtime[0]:
                temp = dtime.pop(0)
                print('  Percentage gereed: '+str(temp))
            count = count+1
        pyl.axis('equal')
        return lhandles


class _BasisLijn_P1P2(_BasisLijnPunt):
    """class methoden voor Lijn-elementen die uit een beginpunt (P1) en eindpunt (P2) bestaan

    In het geval alleen P1 opgegeven wordt,
        dan ligt het eindpunt op m+1 voor V-elementen en op n+1 voor U-elementen
    """
    def _check_LijnP1P2(self):
        #from collections import Counter
        keysp1p2 = ['P1', 'P2', 'name']
        for lijn in self.Lijn:
            for kp1p2 in keysp1p2:
                assert kp1p2 in self.Lijn[lijn]
        #try:
        #    for k, v in self.Lijn.iteritems():
        #        self.Lijn[k]['P1']
        #        self.Lijn[k]['P2']
        #        self.Lijn[k]['name']
        #        #self.Lijn[k].has_key('utype')
        #        #self.Lijn[k].has_key('vtype')
        #except KeyError, Argument:
        #    print('ontbrekende key in dictionary', Argument)
        #    raise
        #except AttributeError, Argument:
        #    print('geen punt dictionary?', Argument)
        #    raise

    #@classmethod
    def add_punt(self, punt,):
        """haal punt-info op uit puntenlijst of Punt-instance en voeg deze aan opening-object
        Input:
            punt
                a) list met Punten (ingelezen met inl_waqua)
                b) waquagrid_toolkit.Punt - instance.
        Output:
            Update van Lijn
        """
        if hasattr(punt, 'Punt'):
            punt = punt.Punt
        else:
            raise NotImplementedError
        #elif isinstance(punt, str):
        #    assert(arg != ()), 'geef pad op met punten file'
        #    temp = wgtk.Punt(punt, arg[0])
        #    punt = temp.Punt
        for k in self.Lijn:
            p_1 = self.Lijn[k]['P1']
            p_2 = self.Lijn[k]['P2']
            if punt[p_1]['n'] == punt[p_2]['n']:
                vtype = 2
                utype = 0
            elif punt[p_1]['m'] == punt[p_2]['m']:
                vtype = 0
                utype = 1
            else:
                raise Exception
            self.Lijn[k].update({'L1':[punt[p_1]['m'], punt[p_1]['n']]})
            self.Lijn[k].update({'L2':[punt[p_2]['m'], punt[p_2]['n']]})
            self.Lijn[k].update({'utype':utype})
            self.Lijn[k].update({'vtype':vtype})
        self.plot_naam = self._plot_naam
