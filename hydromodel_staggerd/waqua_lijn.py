import os
import numpy as np
import pylab as pyl
import plottools as pt
#from waquagrid_toolkit import _handling_axeskwargs, list_methods
from modellijn import _BasisLijn, _BasisLijn_P1P2, _handling_axeskwargs
#from modelpuntlijn import _BasisLijnPunt
#import waquagrid_toolkit_test as wgtk

class Opening(_BasisLijn, _BasisLijn_P1P2):
    """    class met Lijnelementen Opening"""
    def __init__(self, ofile, opad):
        """Input:
            - ofile= naam Opening file (string)
            - opad = naam Opening pad (string)
        Output:
            Opening Line instance
        """
        print('class Opening ')
        from inl_waqua import lijn as inl
        opening = inl().opening(ofile, opad)
        self.Lijn = opening
        self._check_LijnP1P2()

    def add_boundary(self, bfile, bpad):
        """haal punt op uit boundaryfile en voeg deze aan opening-object
        Input:
            - bfile= naam boundary-file (string)
            - bpad = naam boundary-pad  (string)
        Output:
            Update attribuut Lijn met info uit boundary.
        """
        from inl_waqua import lijn as inl
        boundary = inl().boundary(bfile, bpad)
        boundarynr = boundary.keys()
        openingnr = self.Lijn.keys()
        openingsel = set.intersection(set(boundarynr), set(openingnr))
        for k in openingsel:
            self.Lijn[k].update({'boundary':boundary[k]})
        self.plot_openingtype = self._plot_openingtype


    def _plot_openingtype(self, xveld=None, yveld=None, *args, **kwargs):
        """ Plot in kaartje informatie over de boundary.
        Voordat gebruik moet je eerst de methoden add_punt en add_boundary gedaan hebben
        Input:
            - xveld = x-coordinaten, None of array ter grootte van model
            - yveld = y-coordinaten, None of array ter grootte van model
            - *args en **kwargs: zie matplotlib.text
        Output:
            kaartje met info openingen in een kaartje
        """
        #kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, xveld, yveld)

        self._check_lijn()
        for klijn in self.Lijn:
            assert('boundary' in self.Lijn[klijn]), \
                "eerst type rvw toevoegen met add_boundary!"
            assert('L1' in self.Lijn[klijn]), \
                "eerst punt toevoegen met add_punt"
            m_l = self.Lijn[klijn]['L1'][0]
            n_l = self.Lijn[klijn]['L1'][1]
            btype = self.Lijn[klijn]['boundary']['btype']
            #n_l = self.Lijn[klijn]['L1'][klijn]
            #naam = self.Lijn[l]['name']
            if xveld is None:
                pyl.text(m_l, n_l, btype, *args, **kwargs)
            else:
                pyl.text(xveld[m_l-1, n_l-1], yveld[m_l-1, n_l-1], btype, **kwargs)

class Curve(_BasisLijn, _BasisLijn_P1P2):
    #class Curve(_BasisLijn_P1P2):
    """class met Lijnelementen Curve"""

    def __init__(self, cfile, cpad):
        """
        Input:
            - cfile= naam curve-file (string)
            - cpad = naam curve-pad  (string)
        Output:
            - Instance curve element"""
        from inl_waqua import lijn as inl
        self.Lijn = inl().curve(cfile, cpad)
        self._check_LijnP1P2()
        #print(dir(self))
        #def alt_plot():
        #    print('voer method \"add punt\" eerst uit!')
        #self.plot_lijn = alt_plot
        #self.return_xy = alt_plot
        #self.return_mn2lijnindex = alt_plot

class Barrier(_BasisLijn, _BasisLijn_P1P2):
    """    class met Lijnelementen Barrier"""

    def __init__(self, bfile, bpad):
        """
        Input:
            - bfile= naam barrier-file (string)
            - bpad = naam barrier-pad  (string)
        Output:
            - Instance barrier object.
        """
        from inl_waqua import lijn as inl
        lijn = inl().barrier(bfile, bpad)
        self.Lijn = lijn
        self._check_lijn()
        #self._check_LijnP1P2()

    def return_defpointcurve(self):
        """Haal curve en lijn object uit het barrierobject
        Output:
            - return 1: p = puntobjecten
            - return 2: c = curveobjecten
        """
        punt = []
        curve = []
        for klijn in self.Lijn:
            if 'P1' in self.Lijn[klijn]:
                punt.append(klijn)
            elif 'C' in self.Lijn[klijn]:
                curve.append(klijn)
        return punt, curve

    def add_puntcurve(self, curves):
        plist, clist = self.return_defpointcurve()
        if clist != []:
            #if isinstance(curves, wgtk.Curve):
            #    curves = curves
            #else:
            #    raise Exception
            for curvenr in clist:
                cnr = self.Lijn[curvenr]['C']
                try:
                    curve = curves.Lijn[cnr]
                except:
                    raise 'curves niet compatibel met barrier'

                #if curve.has_key('L1') == False:
                if 'L1' not in  curve:
                    print(curve)
                    raise 'aan curve is nog geen puntinfo toegevoegd'
                print(curve)
                if curve['L1'][1] == curve['L2'][1]: #n
                    vtype = 2
                    utype = 0
                elif curve['L1'][0] == curve['L2'][0]:
                    vtype = 0
                    utype = 1
                else:
                    raise Exception
                self.Lijn[curvenr].update({'L1':[curve['L1'][0], curve['L1'][1]]})
                self.Lijn[curvenr].update({'L2':[curve['L2'][0], curve['L2'][1]]})
                self.Lijn[curvenr].update({'utype':utype})
                self.Lijn[curvenr].update({'vtype':vtype})
        else:
            print('Barrier is opgebouwd uit punten in plaats van curves')

class Schotje(_BasisLijn):
    """class met Lijnelementen Curve"""
    def __init__(self, sfile, spad):
        """
        Input:
            - sfile= naam schotjes-file (string)
            - spad = naam schotjes-pad  (string)
        Output:
            Instance schotje element. """
        from inl_waqua import lijn as inl
        lijn = inl().closeuv(sfile, spad)
        self.Lijn = lijn
        self._check_lijn()


class Overlaat(_BasisLijn):
    """class met Lijnelementen Overlaat"""
    def __init__(self, ofile, opad, mnminmax=[0, 0, np.inf, np.inf]):
        """
        Input:
            - ofile= naam overlaat-file (string)
            - opad = naam overlaat-pad  (string)
            - mnminmax = bereik coordinaten waarbinnen de overlaten geplot worden.
        Output:
            Instance Overlaat element
        LET OP:
        Sommige modellen bevatten zoveel elementen, dat het te lang duurt
            om alle elementen in te lezen.
        Dit is de reden, dat mnminmax opgegeven kan worden."""
        from inl_waqua import punt as inl
        self.parameters = {'uv':[['g', 'groyne'],\
                            ['o', 'overflow height'], \
                            ['su', 'sill up'], \
                            ['sd', 'sill down'], \
                            ['cl', 'crest length'], \
                            ['tu', 'talud up'], \
                            ['td', 'talud down']], \
                           'beid':[['veg', 'vegetation type'], \
                            ['cd1', 'first calibration factor Villemont'], \
                            ['cd2', 'second calibration factor Villemont'], \
                            ['vttype', 'weirmodel, Villemont or Tabellenboek']]\
                            }
        overlaat = inl().overlaat(ofile, opad, mnminmax)
        self.Lijn = overlaat
        self._check_lijn()

    def check_overlaattype(self):
        """controleer voor alle lijnelementen of overlaattype correct is
        Voorkomende fouten kunnen zijn
        - utype = 2
        - vtype = 1
        - voor lijnelem van type 3, 4, 5 of 6 zijn geen corresp. lijnelem. aanwezig
        - voor lijnelem van type 3, 4, 5 of 6 heeft het corresp lijnelem. een ander getal.
        Input:
            self
        Output
            fouteu: list van indexnummers voor foute waarden utype
            foutev: list van indexnummers voor foute waarden vtype
            nietcorrespu: lists bestaande uit tuple
                tuple element 1= int indexnummer
                tuple element 2= int:indexnummer Lijnelement met niet overeenkomende v-type
                                None indien geen corresponderende Lijn-element
            nietcorrespv: lists bestaande uit tuple
                tuple element 1= (int) indexnummer gecontroleerd op utype
                tuple element 2= (int):indexnummer Lijnelement met niet overeenkomende u-type
                                None indien geen corresponderende Lijn-element
            """
        fouteu = []
        foutev = []
        nietcorrespv = []
        nietcorrespu = []
        for tel in range(len(self.Lijn)):
            u_l = self.Lijn[tel]['utype']
            v_l = self.Lijn[tel]['vtype']
            if u_l not in [0, 1, 3, 4, 5, 6]:
                fouteu.append(tel)
            else:
                if u_l > 1:
                    corresplijn = self._return_correspondoverlaat(tel)
                    if corresplijn[1] is None:
                        nietcorrespv.append((tel, corresplijn[1]))
                    elif self.Lijn[corresplijn[1]]['vtype'] != self.Lijn[tel]['utype']:
                        nietcorrespv.append((tel, corresplijn[1]))
            if v_l not in [0, 2, 3, 4, 5, 6]:
                foutev.append(tel)
            else:
                if v_l > 2:
                    corresplijn = self._return_correspondoverlaat(tel)
                    if corresplijn[0] is None:
                        nietcorrespu.append((tel, corresplijn[0]))
                    elif self.Lijn[corresplijn[0]]['utype'] != self.Lijn[tel]['vtype']:
                        nietcorrespu.append((tel, corresplijn[0]))
        return fouteu, foutev, nietcorrespu, nietcorrespv

    def _return_array(self, parameter):
        """Geef terug array met waarden voor eigenschap van overlaten.
        Input
            parameter Eigenschap overlaat (string uit verzameling: 'o', 'sd', 'su', 'g').
            Zie inl_waqua voor betekenis
        Output
            array 1D, met eigenschappen van overlaat."""

        parameterlist = ('o', 'sd', 'su', 'g')
        assert parameterlist.count(parameter) == 1, 'Kies parameter uit: '+str(parameterlist)
        data = np.array([], dtype=float)
        data = np.zeros(len(self.Lijn))
        tel = 0
        for lijn in self.Lijn:
            if lijn['utype'] == 0 and lijn['vtype'] > 2:
                continue
            if lijn['vtype'] != 0:
                data[tel] = lijn['v_'+parameter]
            #    lijn.append(uvtype[L['vtype']])
            if lijn['utype'] != 0:
                data[tel] = lijn['u_'+parameter]
            #    lijn.append(uvtype[1])
            #if L['utype']>1:
            #    data[x] = L[parameter]
            #    lijn.append(uvtype[L['utype']])
            tel = tel+1
        data = data[0:tel]
        return data

    def plot_lijnkleur(self, xveld, yveld, param, **kwargs):
        """ Plot lijn met kleurenschaal afhankelijk van parameter waarden
        Input
            - xveld = x-coordinaten, None of array ter grootte van model
            - yveld = y-coordinaten, None of array ter grootte van model
            - param Eigenschap overlaat
                (string uit verzameling: 'o', 'sd', 'su', 'g'). Zie inl_waqua voor betekenis
            - **kwargs = zie matplotlib.plot
        Output
            a) kaartje met lijnen kleur afhankelijk van waarde voor opgegeven parameter.
            b) return 1, h = > handles naar lijnelementen,
            c) return 2, lab = > waarde van parameter, horden bij lijnelement.
        """
        #import plottools as pt
        #kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, xveld, yveld)
  
        data = self._return_array(param)
        scalarmap = pt.SvaLine().lcolormap(data, )
        xyplot = self.return_xy(xveld, yveld)
        #lhandles = []

        #for a in range(len(xy)):
        for xy_l in enumerate(len(xyplot)):
            colorval = scalarmap.to_rgba(data[xy_l[0]])
            pyl.plot(xy_l[1][:, 0], xy_l[1][:, 1], color=colorval, **kwargs)
            #lhandles.append(h[0])
            #x = x+1
 
        legend = pt.SvaLine().legend_lcolormap(scalarmap, 8)
        handlelist = []
        lab = []
        axlim = pyl.axis()
        for leg in legend:
            phandle = pyl.plot(0, 0, color=leg.values()[0], label=str(leg.keys()[0]))
            handlelist.append(phandle[0])
            lab.append('{:.2f}'.format(leg.keys()[0]))

        pyl.legend(handlelist, lab)
        pyl.axis(axlim)
        return handlelist, lab

    def make_overlaatfile(self, ofile, opad):
        """Maak overlaatfile uit attribuut Lijn.

        Input:
            - ofile = naam overlaatfile [string]
            - opad = pad overlaatfile [string]
        Output:
            File in bestandsformaat Box [Ascii]
        Afhankelijkheid binnen module:
            nvt
        """
        volgordeparam = ('u_o', 'u_su', 'u_sd',
                         'v_o', 'v_su', 'v_sd',
                         'u_g', 'v_g',
                         'utype', 'vtype',
                         'u_cl', 'u_tu', 'u_td',
                         'v_cl', 'v_tu', 'v_td',
                         'veg', 'cd1', 'cd2', 'vttype'
                        )
        g_handle = open(os.path.join(opad, ofile), 'w')
        for lijn in self.Lijn:
            g_handle.write('W:' + '{:6d}'.format(lijn['L1'][0]) + '{:6d}'.format(lijn['L1'][1]))
            for par in volgordeparam:
                if lijn[par] is None:
                    break
                if par in ['u_g', 'v_g']:
                    g_handle.write(' \''+lijn[par]+ '\'')
                else:
                    if isinstance(lijn[par], float):
                        g_handle.write('{:>8.2f}'.format(lijn[par]))
                    if isinstance(lijn[par], np.int):
                        g_handle.write(' '+str(lijn[par]))
            g_handle.write('\n')
        g_handle.close()

    def set_typezero(self, lijnnr, uvt):
        """
        Zet vtype of utype van een lijnelement naar 0.
        Input:
            - lijnr = indexnr lijnelement [int]
            - uvt = 'utype' / 'vtype' [string]
        Output:
            Aanpassing aan self.Lijn
        """

        typenr = self.Lijn[lijnnr][uvt]
        m_l, n_l = self.Lijn[lijnnr]['L1']

        if typenr in [0, 1, 2]:
            self.Lijn[lijnnr][uvt] = 0
        elif typenr == 5:
            #overlaattype = 5: zowel vtype als utype aanpassen
            self.Lijn[lijnnr]['vtype'] = 0
            self.Lijn[lijnnr]['utype'] = 0
        else:
            #overlaattype= 3, 4 of 6: corresponderende overlaat aanpassen
            if uvt == 'vtype':
                m_lc = m_l-self.uvtype[typenr][0][0]
                n_lc = n_l-self.uvtype[typenr][0][1]
                typecorrespond = 'utype'
                #if self.Lijn[lijnnr]['vtype'] == 3:
                #    m_lc = m_l-1
                #    n_lc = n_l+1
                #elif self.Lijn[lijnnr]['vtype'] == 4:
                #    m_lc = m_l
                #    n_lc = n_l+1
                #elif self.Lijn[lijnnr]['vtype'] == 6:
                #    m_lc = m_l-1
                #    n_lc = n_l
                #else:
                #    raise Exception( self.Lijn[lijnnr]['vtype'])
            elif uvt == 'utype':
                m_lc = m_l+self.uvtype[typenr][0][0]
                n_lc = n_l+self.uvtype[typenr][0][1]
                typecorrespond = 'vtype'
                #if self.Lijn[lijnnr]['utype'] == 3:
                #    m_lc = m_l+1
                #    n_lc = n_l-1
                #elif self.Lijn[lijnnr]['utype'] == 4:
                #    m_lc = m_l
                #    n_lc = n_l-1
                #elif self.Lijn[lijnnr]['utype'] == 6:
                #    m_lc = m_l+1
                #    n_lc = n_l
                #else:
                #    raise Exception( self.Lijn[lijnnr]['vtype'])
            tel = 0
            try:
                while [self.Lijn[tel]['L1'][0], self.Lijn[tel]['L1'][1]] != [m_lc, n_lc]:
                    if tel == len(self.Lijn[tel]):
                        tel = lijnnr
                        break
                    tel = tel+1
            except:
                raise
            if typecorrespond == 'utype':
                self.Lijn[tel]['utype'] = 0
                self.Lijn[lijnnr]['vtype'] = 0
            elif typecorrespond == 'vtype':
                self.Lijn[tel]['vtype'] = 0
                self.Lijn[lijnnr]['utype'] = 0

    def set_uvparameter(self, lijnnr, paramdict):
        """
        Verander parameters bij een vtype of utype parameter.
        Input:
            - lijnr = indexnr lijnelement [int]
            - paramdict = aan te passen waarden,
                        overeenkomend met inhoud self.Lijn['L1'][i]  [dict]
        Output:
            Aanpassing aan self.Lijn
        N.B. voor overlaten van v-type >2 geldt dat een corresponderende
            u-type ook aangepast moet worden. Dit geldt ook omgekeerd voor
            u-type >1

        """
        #x = lijnnr
        if 'utype' in paramdict:
            assert(paramdict['utype'] != 2), 'utype van lijnnummer '+str(lijnnr) + ' == 2:' \
                'dit type is gereserveerd voor v-type'
        if 'vtype' in paramdict:
            assert(paramdict['vtype'] != 1), 'utype van lijnnummer '+str(lijnnr) + ' == 1:' \
                'dit type is gereserveerd voor u-type'

        for k in paramdict:
            if k in ['cd1', 'cd2', 'veg', 'vttype']:
                self.Lijn[lijnnr][k] = paramdict[k]#.pop(k)#paramdict[k]
        #inputcheck = set()
        for k in paramdict:
            if k not in ['cd1', 'cd2', 'veg', 'vttype']:
                uvtype = k[0]
                break
        assert uvtype == 'u' or uvtype == 'v', ' verkeerde invoer paramdict'
        ucorresp, vcorresp = self._return_correspondoverlaat(lijnnr)
        if uvtype == 'v':
            if ucorresp is not None:
                ucorresp2, vcorresp2 = self._return_correspondoverlaat(ucorresp)
                if vcorresp2 is None:
                    self.Lijn[lijnnr]['vtype'] = paramdict['vtype']
                    self.Lijn[ucorresp]['utype'] = paramdict['vtype']
                #else:
                #    self.set_typezero(vcorresp2, 'vtype')
                #if paramdict['vtype'] == 1:
                #    raise
                if self.Lijn[ucorresp]['utype'] == 2:
                    self.Lijn[ucorresp]['utype'] = 0
        else:# uvtype == 'u':
            if vcorresp is not None:
                ucorresp2, vcorresp2 = self._return_correspondoverlaat(vcorresp)
                if ucorresp2 is None:
                    self.Lijn[lijnnr]['utype'] = paramdict['utype']
                    self.Lijn[vcorresp]['vtype'] = paramdict['utype']
                #else:
                #    self.set_typezero(ucorresp2, 'utype')
                #if paramdict['utype'] == 2:
                #    raise
                #print(vcorresp)
                if self.Lijn[vcorresp]['vtype'] == 1:
                    self.Lijn[vcorresp]['vtype'] = 0
        #parameterlist = self.parameters['uv']
        for par in self.parameters['uv']:
            param = uvtype+'_'+par[0]
            #print(param)
            if  param in paramdict:
                aanpaswaarde = paramdict[param]
            else:
                aanpaswaarde = self.Lijn[lijnnr][param]
            self.Lijn[lijnnr][param] = aanpaswaarde
            if ucorresp is not None:
                self.Lijn[ucorresp][param] = aanpaswaarde
            elif vcorresp is not None:
                self.Lijn[vcorresp][param] = aanpaswaarde

    def _return_correspondoverlaat(self, lijnnr):#, vu = None):
        #x = lijnnr
        #m = self.Lijn[x]['L1'][0]
        #n = self.Lijn[x]['L1'][1]
        #if vu is None:
        #vt = self.Lijn[x]['vtype']
        #ut = self.Lijn[x]['utype']
        #elif vu[0] == 'v':
        #    vt = self.Lijn[x]['vtype']
        #    ut = None;
        #elif vu[0] == 'u':
        #    ut = self.Lijn[x]['utype']
        #    vt = None
        #else:
        #    raise
        #if vt is not None:
        if self.Lijn[lijnnr]['vtype'] == 1:
            self.Lijn[lijnnr]['vtype'] = 0
            #raise Exception
        if self.Lijn[lijnnr]['vtype']in [0, 2]:
            ucorresp = None
        elif self.Lijn[lijnnr]['vtype'] == 5:
            #overlaattype = 5: zowel vtype als utype aanpassen
            ucorresp = lijnnr
        else:
            vtypenr = self.Lijn[lijnnr]['vtype']
            m_c = -self.uvtype[vtypenr][0][0]
            n_c = -self.uvtype[vtypenr][0][1]

            #if self.Lijn[x]['vtype'] == 3:
            #    mc = self.UVtype[3][0][0]
            #    nc = self.UVtype[3][0][1]
            #    #mc = m-1;nc = n+1
            #elif self.Lijn[x]['vtype'] == 4:
            #    mc = m;nc = n+1
            #elif self.Lijn[x]['vtype'] == 6:
            #    mc = m-1;nc = n

            tel = 0
            #try:
            while [self.Lijn[tel]['L1'][0], self.Lijn[tel]['L1'][1]] != [m_c, n_c]:
                tel = tel+1
                if tel == len(self.Lijn):
                    tel = None
                    break
            #except:
            #raise Exception( self.Lijn[x]['vtype'])
            ucorresp = tel
        #else:
        #    ucorresp = None
        #if ut is not None:
        if self.Lijn[lijnnr]['utype']in [0, 1]:
            vcorresp = None
        elif self.Lijn[lijnnr]['utype'] == 5:
            #overlaattype = 5: zowel vtype als utype aanpassen
            vcorresp = lijnnr
        else:
            utypenr = self.Lijn[lijnnr]['utype']
            m_c = self.uvtype[utypenr][0][0]
            n_c = self.uvtype[utypenr][0][1]

            #if self.Lijn[x]['utype'] == 3:
            #    mc = m+1;nc = n-1
            #elif self.Lijn[x]['utype'] == 4:
            #    mc = m;nc = n-1
            #elif self.Lijn[x]['utype'] == 6:
            #    mc = m+1;nc = n

            tel = 0
            #try:
            while [self.Lijn[tel]['L1'][0], self.Lijn[tel]['L1'][1]] != [m_c, n_c]:
                tel = tel+1
                if tel == len(self.Lijn):
                    tel = None
                    break
            #except:
            #raise Exception( str(x)+' '+str(self.Lijn[x]['utype']))
            vcorresp = tel
        #else:
        #    vcorresp = None
        return ucorresp, vcorresp


class Ruwheidarea(_BasisLijn):
    """    class met Lijnelementen Ruwheid"""
    def __init__(self, rfile, rpad, uvtype):
        """
        Input:
            - rfile= naam ruwheid-file (string)
            - rpad = naam ruwheid-pad  (string)
            - uvtype=  ['u|v']
        Output:
            - Instance ruwheid object.
        """
        assert uvtype == 'u' or uvtype == 'v', 'uvtype is \'u\' of  \'v\''
        from inl_waqua import punt as inl
        lijntemp = inl().ruwheidarea(rfile, rpad)
        self.Lijn = {}
        tel = 1
        for lijn in lijntemp:
            if uvtype == 'u':
                lijn.update({'utype':1, 'vtype':0})
            elif uvtype == 'v':
                lijn.update({'utype':0, 'vtype':2})
            self.Lijn.update({tel:lijn})
            tel = tel+1
        self._check_lijn()

    def make_ruwheidareafile(self, rfile, rpad):
        g_handle = open(os.path.join(rpad, rfile), 'w')
        for lijn in self.Lijn:
            m_l, n_l = self.Lijn[lijn]['L1']
            rough = self.Lijn[lijn]['roughcode']
            frac = self.Lijn[lijn]['fraction']
            temp = '{:6d}{:6d}{:6d}{:10f}'.format(n_l, m_l, rough, frac)
            g_handle.writelines(temp+'\n')
        g_handle.close()

class Enclosure(object):
    """    class van Enclosure
    Attributen
        - self.mn_coor: list met mn coordinaten van enclosureelementen
        - self.Path: list van enclosure-elementen als matplotlib.path instances
        - self.vertices: list van enclosure-elementen als xy coordinaten"""
    def __init__(self, efile, epad):
        """
        Input:
            - efile= naam enclosure-file (string)
            - bpad = naam enclosure-pad  (string)
        Output:
            Instance enclosure element."""
        from inl_waqua import route as inl
        from matplotlib.path import Path
        enclosure = inl().enclosure(efile, epad)
        self.mn_coor = []
        self.path = []
        for encl in enclosure:
            self.path.append(Path(encl))
            self.mn_coor.append(encl)
        self.vertices = []

    def _cleanencl(self, dummyval=-999):
        """ Dit is vrij suf: soms is er geen goede xy-coordinaat voor een punt op de enclosure.
        Dat geldt in ieder geval xzeta en yzeta velden die gemaakt zijn met getdata.
        Dan moet je bepaalde cellen verwijderen. De enclosure is dan incompleet, maar
        tot nader orde is dit nodig....Helaas. """
        xyenclclean = []
        for vert in self.vertices:
            vert = vert.reshape(-1, 1)
            i = np.where(vert == -999)
            vert2 = np.delete(vert, i[0])
            vert2 = vert2.reshape(-1, 2)
            xyenclclean.append(vert2)        #print(e2.shape)
        self.vertices = xyenclclean        #print(self.vertices[0].shape)

    def return_xycoor(self, xzetaveld, yzetaveld):
        """geef terug xy-coordinaten van de enclosure-elementen
        Input:
            - xzetaveld= x-coordinaten op waterstandspunt. array of wgtk.Sepveld
            - yzetaveld= y-coordinaten op waterstandspunt. array of wgtk.Sepveld
        Output:
            1) update van self.vertices
            2) list van vertices per enclosure-element    """
        def findcells(encl):
            vert1 = encl[0]
            vertarray = None
            for vert in encl[1:]:
                vert2 = vert
                if vert2[0] == vert1[0]:
                    if vert2[1] < vert1[1]:
                        dstep = -1
                    else:
                        dstep = 1
                    n_e = np.arange(vert1[1], vert2[1]+dstep, dstep)
                    m_e = np.array([vert1[0]]*len(n_e))
                else:
                    if vert2[0] < vert1[0]:
                        dstep = -1
                    else:
                        dstep = 1
                    m_e = np.arange(vert1[0], vert2[0]+dstep, dstep)
                    n_e = np.array([vert1[1]]*len(m_e))
                if vertarray is not None:
                    vertarray = np.vstack([vertarray, np.vstack([m_e[0:-1], n_e[0:-1]]).T])
                else:
                    vertarray = np.array([m_e[0:-1], n_e[0:-1]]).T
                vert1 = vert2
            return vertarray

        try:
            from waqua_veld import Sepveld
            if isinstance(xzetaveld, Sepveld) or \
                    isinstance(xzetaveld, Sepveld):
                xveld = xzetaveld.Veld
                yveld = yzetaveld.Veld
            else:
                xveld = xzetaveld
                yveld = yzetaveld
        except:
            raise Exception( type(xzetaveld), type(yzetaveld))

        vertices = []
        self.path = []
        for encl in self.mn_coor:
            vertarray = findcells(encl)
            temp = []
            for tel in range(vertarray.shape[0]):
                temp.append([xveld[vertarray[tel, 0]-1, vertarray[tel, 1]-1], \
                            yveld[vertarray[tel, 0]-1, vertarray[tel, 1]-1]])
                #print(temp)
            vertices.append(np.array(temp, dtype=float))
        self.vertices = vertices
        self._cleanencl()
        return self.vertices

    def plot_lijn(self, xveld=None, yveld=None, *args, **kwargs):
        """ plot lijnelemente in kaartje

        Input:
            - xveld = x-coordinaten, [None of array overeenkomend modelveld]
            - yveld = y-coordinaten, [None of array overeenkomend modelveld]
            - *args en **kwargs: zie matplotlib.plot
        """

        kwargs = _handling_axeskwargs(kwargs, xveld, yveld)
        lhandles = []

        #if len(self.Lijn)>10000 and xveld is not None:
        #    print('Je probeert heel veel lijnen te plotten in xy coordinaten.')
        #    print('Dit kan zeer lang duren.')
        #    print('Overweeg om de lijnstukken in mn-coordinaten te plotten')
        #    pyl.pause(2)

        if xveld is None:
            xyplot = self.mn_coor
        else:
            #xy = self.return_xycoor(xveld, yveld)
            raise Exception( 'nog niet geimplementeerd!')
        #n_lijnstuk = len(xy)
        d_t = [0, 10, 25, 50, 75, 100, 101]
        tel = 0
        print('plot lijn:')
        for xy_l in xyplot:
            try:
                l_handle = pyl.plot(xy_l[:, 0], xy_l[:, 1], *args, **kwargs)
            except:
                print('Fail in:'+self+'->'+str(xy_l))
            lhandles.append(l_handle[0])
            if (float(tel)/len(xyplot))*100. > d_t[0]:
                tim = d_t.pop(0)
                print('  Percentage gereed: '+str(tim))
            tel = tel+1
        pyl.axis('equal')
        return lhandles
