import os
import numpy as np
import pylab as pyl
import plottools as pt
#from waquagrid_toolkit import _handling_axeskwargs
from modelpuntlijn import _BasisLijnPunt, _handling_axeskwargs

class Dam(object):
    """class van Dam

    Attributen
        self.Dam """
    def __init__(self, dfile, dpad):
        """
        Input:
            - dfile= naam dam-file (string)
            - dpad = naam dam-pad  (string)
        Output:
            Instance dam element."""
        from inl_waqua import punt as inl
        dam = inl().dam(dfile, dpad)
        self.Dam = dam

    def return_xy(self, xzeta=None, yzeta=None):
        """
        input:
            xzeta, yzeta: array of NONE.
        Output:
            List met array bestaande uit coordinaten beginpunt en eindpunt"""

        xyreturn = []
        if xzeta is None:
            for dam in self.Dam:
                xyreturn.append([float(dam[0])-0.5, float(dam[1])-0.5])
        else:
            for dam in self.Dam:
                xyreturn.append([xzeta[dam[0]-1, dam[1]-1], yzeta[dam[0]-1, dam[1]-1]])
                #, yzeta[d[0]-1, d[1]-1])
        return np.array(xyreturn)

    def plot_dam(self, xzeta=None, yzeta=None, **kwargs):
        """ plot lijn dam"""
        #kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, xzeta, yzeta)
        xyplot = self.return_xy(xzeta, yzeta)
        pyl.plot(xyplot[:, 0], xyplot[:, 1], 'rx', xyplot[:, 0], xyplot[:, 1],\
                 'rs', markersize=3, **kwargs)

class Punt(_BasisLijnPunt):
    """class van Punt

    Attributen
        self.Punt
    """

    def __init__(self, pfile, ppad):
        """
        Input:
            - pfile= naam punt-file (string)
            - ppad = naam punt-pad  (string)
        Output:
            Instance dam element."""
        if isinstance(pfile, str):
            from inl_waqua import punt as inl

            punt = inl().point(pfile, ppad)
            #print('nieuwe class maken uit "Punt" dictionary afkomstig van inl_waqua')
            try:
                for pkey in punt.keys():
                    'm' in punt[pkey]
                    'n' in punt[pkey]
                    'name' in punt[pkey]
            except KeyError as Argument:
                print('ontbrekende key in dictionary', Argument)
            except AttributeError as Argument:
                print('geen punt dictionary?', Argument)
            if len(set(punt)) < len(punt):
                raise ValueError
            name = []
            for pkey in punt:
                name.append(punt[pkey]['name'])
            if len(set(name)) < len(punt):
                print('dubbele naam in list')
            #else:
            #    punt = {}
        else:
            if pfile.__class__.__name__ == self.__class__.__name__:
                punt = pfile
            else:
                raise TypeError('Nasty')
        self.Punt = punt
        #self.plot_naam = self._plot_naam

    def __getitem__(self, key):
        """
        Slicing laten werken op attribuurt Veld.
        """
        return self.Punt[key]

    def plot_naam(self, *arg, **kwarg):
        self._plot_naam(*arg, **kwarg)

    def _return_xyboxselect(self, xybox):
        """return punten op _Basis van xy-coordinaten

        Input:
            xybox: list met coordinaten. [xmin, xmax, ymin, ymax]
        Output:
            geselecteerde punten, list met dictionaries"""

        xmin = xybox[0]
        xmax = xybox[1]
        ymin = xybox[2]
        ymax = xybox[3]
        puntsel = {}
        #assert xmin<xmax & ymin<ymax, str(xmin)+str(xmax)+str(ymin)+str(ymax)
        for pkey in self.Punt:
            if self.Punt[pkey]['x'] > xmin and self.Punt[pkey]['x'] < xmax and \
                self.Punt[pkey]['y'] > ymin and self.Punt[pkey]['y'] < ymax:
                puntsel[pkey] = self.Punt[pkey]
        return puntsel


    def return_puntlist(self):
        """return punten als list

        Output:
            geselecteerde punten, list met dictionaries
        """
        nr = []
        name = []
        x = []
        y = []
        m = []
        n = []
        for p in self.Punt:
            nr.append(p)
            name.append(self.Punt[p]['name'])
            m.append(self.Punt[p]['m'])
            n.append(self.Punt[p]['n'])
            if 'x' in self.Punt[p]:
                x.append(self.Punt[p]['x'])
                y.append(self.Punt[p]['y'])
        return nr, name, m, n, x, y

    def add_xy(self, xveld, yveld):
        """haal coordinaten van punten op uit een x en y-velden voeg deze toe aan punt-object

        Input:
            - xveld: veld met x-coordinaten, array
            - yveld: veld met y-coordinaten, array
        Output:
            x- en y-attribuut toegevoegd aan self.Punt
        """
        for pkey in self.Punt:
            #print(p)
            m_p = self.Punt[pkey]['m']
            n_p = self.Punt[pkey]['n']
            self.Punt[pkey]['x'] = xveld[m_p-1, n_p-1]
            self.Punt[pkey]['y'] = yveld[m_p-1, n_p-1]
        self.return_xyboxselect = self._return_xyboxselect

    def add_punt(self, puntnr, m_p, n_p, naam):
        """Toevoegen van punt aan Punt attribuut """
        assert(puntnr not in self.return_puntlist()[0]), 'Puntnummer reeds in Punt-object'
        assert(naam not in self.return_puntlist()[1]), 'Puntnaam reeds in Punt-object'
        self.Punt.update({puntnr:{'m':m_p, 'n':n_p, 'name':naam}})

    def contr_checkpoint(self, checklist):
        """controleer of Points in lijst met checkpoints voorkomen

        Input:
            checkl: lijst met checkpoint nummers, iterable
        Output
            naar standaard output (scherm)
        """
        ontbrekend = []
        for check in checklist:
            assert(isinstance(check, int)), " checkpointlist bevat non-integers"
            if not check in self.Punt:
                ontbrekend.append(check)
        #if len(ontbrekend) == 0:
        if ontbrekend:
            print('Geen ontbrekende points in pointfile')
        else:
            print('volgende puntennummers ontbreken in poinstfile tov checkpoint')
            print(ontbrekend)

    def print_naam(self):
        """print(puntnamen naar scherm)
        Output:
            naar standaard output (scherm)"""
        puntlist = self.return_puntlist()[0]
        for punt in puntlist:
            print(self.Punt[punt]['name'])

    def make_puntfile(self, pfile, ppad, cfile=None):
        self.write_puntfile(pfile, ppad, cfile)

    def write_puntfile(self, pfile, ppad, cfile=None):
        """maak puntenfile,

        Input:
            - pfile= naam puntfile, string
            - ppad =naam pad puntfile, string
            - cfile = naam pad puntfile, None/string
        Output:
            puntenfile en eventueel checkpoint file"""

        g_handle = open(os.path.join(ppad, pfile), 'w')
        pnummerlist = self.return_puntlist()[0]
        pnummerlist.sort()
        for pkey in pnummerlist:
            #pnr = v
            naam = self.Punt[pkey]['name']
            m_p = self.Punt[pkey]['m']
            n_p = self.Punt[pkey]['n']
            #for p, v in self.Punt.iteritems():
            #    pnr = v
            #    naam = v['name']
            #    m = v['m']
            #    n = v['n']
            g_handle.write('P'+ str(pkey) +'= (m= ' + str(m_p) +  ', n ' + str(n_p)+ \
                ', name = \'' + naam +'\')\n')
        g_handle.close()

        if cfile is not None:
            g_handle = open(cfile, 'w')
            tel = 1
            for pkey in pnummerlist:
                g_handle.write(str(pkey)+', ')
                tel = tel+1
                if tel == 11:
                    g_handle.write('\n')
                    tel = 1
            g_handle.close()

    def plot_punt(self, *arg, **kwarg):
        """    Plot punten naar een kaartje

        Input:
            * Optie 1: Plot in xy-coordinaten, met opgegeven x- en y-veld
                - arg1 = xveld,
                - arg2 = yveld,
                - arg3 e.v: argumenten plot
                - kwargs= keyword kwargumenten plot
            * Optie 2: Plot in xy, met x, y coordinaten uit attribuut Punt
                - arg1 = True,
                - kwargs = keyword argumenten plot
            * Optie 3: Plot in mn coordinaten
                - arg1 ev = argumten plot
                - kwargs = keyword argumenten plot

            Output:
                kaartje met punten."""

        if not arg:
            plotxy = False
            plotxy = False
            veldxy = False
            inputarg = ['k.']
        elif issubclass(type(arg[0]), np.ndarray):
            kwarg = _handling_axeskwargs(kwarg, arg[0], arg[1])
            plotxy = True
            veldxy = True
            xveld = arg[0]
            yveld = arg[1]

            #ax = pt.SvaAxis.autodetermineplotaxis(xveld, yveld)
            #kwargs.update({'axes':ax})
            if len(arg) >= 3:
                inputarg = arg[2:]
            else:
                inputarg = ['k.']
        elif arg[0] is True:
            plotxy = True
            veldxy = False
            if len(arg) > 1:
                inputarg = arg[1:]
            else:
                inputarg = ['k.']
        else:
            raise Exception
        for pkey in self.Punt:
            pval=self.Punt[pkey]
            if plotxy is False:
                xplot = pval['n']
                yplot = pval['m']
            else:
                if veldxy is False:
                    xplot = float(pval['x'])
                    yplot = float(pval['y'])
                else:
                    xplot = xveld[pval['m'], pval['n']]
                    yplot = yveld[pval['m'], pval['n']]
            pyl.plot(xplot, yplot, *inputarg, **kwarg)

    def compare_puntobject(self, puntobj):
        """vergelijk de puntNUMMERS uit een ander puntobject

        Input:
            * wgtk.Punt-object
        Output:
            set met verschillende
        """
        setself = set(self.Punt)
        setinput = set(puntobj)
        return set.difference(setself, setinput)
