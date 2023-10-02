#import os
import numpy as np
import pylab as pyl
import plottools as pt
#from waquagrid_toolkit import _handling_axeskwargs
from modelveld import _BasisVeldFunc, _BasisVeldPlot, _handling_axeskwargs
#import waquagrid_toolkit as wgtk


class Depveld(_BasisVeldPlot):
    """ Object voor veld, dat gedefinieerd is op diepte punten
    Methoden
        mask_dep_value, mask_dep_masker uit mask_waquaveld
    """
    def __init__(self, *arg):
        """
        Input:
            arg: opties
                a) 1 argument => [numpy array]
                b) 2 argument => a)filenaam[string], b)pad[string]
                c) 3 argumenten=>
                    1)filenaam[string], 2)pad[string] , 3)filetype[string=>'box'|'matfile']
        Output:
            Depveld-object
        Afhankelijkheid binnen module:
            nvt
        """
        print(__name__)

        _BasisVeldFunc.__init__(self, *arg)

        from mask_staggerdveld import mask_dep_value, mask_dep_masker
        self.return_plotmask = mask_dep_masker
        self.return_valuemask = mask_dep_value

    def __sub__(self, depobj):
        #print(dir(self))
        #return wgtk.Depveld(self.Veld-depobj.Veld)
        return self.__init__(self.Veld-depobj.Veld)

    def return_dep2wat(self):
        """Interpoleer vanuit bodempunt naar waterstandspunt

        Output:
            waarde op waterstandpunt: masked array
        """
        wat = self._return_veldaverage()
        y_0 = np.ma.masked_equal(np.zeros([1, wat.shape[1]]), 0)
        wat = np.ma.vstack([y_0, wat])
        x_0 = np.ma.masked_equal(np.zeros([wat.shape[0], 1]), 0)
        wat = np.ma.hstack([x_0, wat])
        return wat
    """
    def _return_xyplot(self, xbase, ybase):
        #from waqua_veld import Depveld, Rgfveld, Sepveld
        if isinstance(xbase, np.ma.MaskedArray):
            print('ggg')
            assert isinstance(ybase, np.ma.MaskedArray), \
                    'xbase en ybase zijn niet zelfde type! xbase = '\
                    +type(xbase)+', ybase = '+type(ybase)
            xplot = xbase
            yplot = ybase
        else:
            xclassname = xbase.__class__.__name__()
            yclassname = ybase.__class__.__name__()
            #if isinstance(xclassname, Rgfveld):
            if xclassname == 'Rgfveld':
                xplot, yplot = xbase.return_dep2wat()
            #elif isinstance(xbase, Depveld):
            elif xclassname == 'Depveld':
                assert yclassname == xclassname, \
                    'xbase en ybase zijn niet zelfde type! xbase = '\
                    +xbase+', ybase = '+ybase
                xplot = xbase.return_dep2wat()
                yplot = ybase.return_dep2wat()
                #z= self.return_plotveld(xplot)
            elif xclassname == 'Sepveld':#elif isinstance(xbase, Sepveld):
                assert yclassname == xclassname, \
                    'xbase en ybase zijn niet zelfde type! xbase = '\
                    +xbase+', ybase = '+ybase
                xplot = xbase.Veld
                yplot = ybase.Veld
            else:
                raise Exception( 'Ongeldig invoer voor xbase')
        return xplot, yplot
    """
 
    def pcolor(self, xbase=None, ybase=None, ax_h=None, colorbar=True, *args, **kwargs):
        if xbase is not None:
            print(xbase)
            #plot veld zonder xy- coordinaten
            xplot, yplot = self._return_xyplot(xbase, ybase)
        cb_handle = self._pcolor(xplot, yplot, ax_h, colorbar, *args, **kwargs)
        return cb_handle


    def pcolor_new(self, xbase=None, ybase=None, ax_h=None, colorbar=True, *args, **kwargs):
        if xbase is not None:
            #print(xbase)
            #plot veld zonder xy- coordinaten
            xplot, yplot, xymasker = self._return_xyplot(xbase, ybase)
            xplot=np.ma.array(xplot,mask=xymasker)
            yplot=np.ma.array(yplot,mask=xymasker)
        else:
            xplot = xbase
            yplot = ybase

        #if ybase!=None:
        #    axlim = self._return_xylim(xplot, yplot)
        #else:
        #    xtemp=xbase.Xdep.Veld
        #    ytemp=xbase.Ydep.Veld
        #    axlim = self._return_xylim(xtemp, ytemp)
        axlim = self._return_xylim(xplot, yplot)
        pyl.axis(axlim)#axlim = self._return_xylim(xplot, yplot)

        cb_handle = self._pcolor_new(xplot, yplot,xymasker, ax_h, colorbar, *args, **kwargs)
        return cb_handle

    def contourf(self,xbase=None, ybase=None,  nr_klasse=None, ax_h=None, colorbar=True, *args, **kwargs):
        if xbase is not None:
            #print(xbase)
            #plot veld zonder xy- coordinaten
            xplot, yplot, xymasker = self._return_xyplot(xbase, ybase)
        else:
            xplot = xbase
            yplot = ybase
        #axlim = self._return_xylim(xbase, ybase)
        #pyl.axis(axlim)#axlim = self._return_xylim(xplot, yplot)

        cb_handle = self._contourf(xplot, yplot ,xymasker, nr_klasse, ax_h, colorbar, *args, **kwargs)
        return cb_handle
#class Coppreveld(_BasisVeldPlot):
#    def __init__(self, filenaam, pad):
#        """
#        Input:
#            arg: opties
#                a) 1 arg. => [numpy array]
#                b) 2 arg. => a)filenaam[string], b)pad[string]
#                c) 3 arg, => 1)filenaam[string], 2)pad[string] , 3)filetype
#                   opties filetype => [string=>'box'|'matfile'|'coppre']
#        Output:
#            Depveld-object
#        Afhankelijkheid binnen module:
#            nvt
#        """
#        _BasisVeldFunc.__init__(self, filenaam, pad)
#        raise NotImplementedError


class Rgfveld(object):
    """class Rgf-object.

    Opgebouwd uit 2 velden: 1) Veld met  x-coordinaten 2) Veld met y-coordinaten\n
    Beiden op dieptepunt
    Attributen
        - self.Xdep (Depveld-object)
        - self.Ydep (Depveld-object
    Externe Methoden
        - roostereigenschappen uit info_waquaveld
        - veldstatindex uit info_waquaveld
    """
    def __init__(self, inp1, inp2):
        #from waquagrid_toolkit import _BasisVeldFunc
        import info_waquaveld
        from inl_waqua import veld as inl
        from mask_staggerdveld import mask_dep_value, mask_dep_masker

        assert isinstance(inp1, (str, np.ma.MaskedArray))

        if isinstance(inp1, str):
            vfile = inp1
            vpad = inp2
            xdep, ydep = inl().rgf(vfile, vpad)
        else:
            xdep = inp1
            ydep = inp2
        self.Xdep = _BasisVeldFunc(xdep)
        self.Ydep = _BasisVeldFunc(ydep)
        print('gggg')
        print(self.Xdep)
     
        #print('yes1')
        #self.Xdep._ini_veldobj(rgf[0])
        #print('yes2')
        #self.Ydep._ini_veldobj(rgf[1])
        self.Xdep.return_valuemask = mask_dep_value
        self.Xdep.return_plotmask = mask_dep_masker
        self.Ydep.return_valuemask = mask_dep_value
        self.Ydep.return_plotmask = mask_dep_masker
        self.roostereigenschappen = \
            info_waquaveld.roostereigenschappen(self.Xdep.Veld, self.Ydep.Veld)
        self.Xdep.veldstatindex = info_waquaveld.veldstatistiek.index(self.Xdep.Veld)
        self.Ydep.veldstatindex = info_waquaveld.veldstatistiek.index(self.Ydep.Veld)

    def return_dep2wat(self):
        """Interpoleer vanuit bodempunt naar waterstandspunt
        Output:
            x en y op waarde op waterstandpunt: 2*masked array
        """

        xwat = self.Xdep._return_veldaverage()
        y_0 = np.ma.masked_equal(np.zeros([1, xwat.shape[1]]), 0)
        xwat = np.ma.vstack([y_0, xwat])
        x_0 = np.ma.masked_equal(np.zeros([xwat.shape[0], 1]), 0)
        xwat = np.ma.hstack([x_0, xwat])
        ywat = self.Ydep._return_veldaverage()
        #y = np.ma.masked_equal(np.zeros([1, ywat.shape[1]]), 0)
        ywat = np.ma.vstack([y_0, ywat])
        #y = np.ma.masked_equal(np.zeros([ywat.shape[0], 1]), 0)
        ywat = np.ma.hstack([x_0, ywat])
        return xwat, ywat

    def return_dep2vel(self):
        """Interpoleer vanuit bodempunt naar waterstandspunt

        Output:
            x en y op waarde op stroomsnelheidpunt: 2*masked array
        """
        xdep_vel = self.Xdep.Veld[0:-1, 0:-1]*1/3+self.Xdep.Veld[1:, 1:]*2/3
        ydep_vel = self.Ydep.Veld[0:-1, 0:-1]*1/3+self.Ydep.Veld[1:, 1:]*2/3
        y_0 = np.ma.masked_equal(np.zeros([1, self.Xdep.Veld.shape[1]-1]), 0)
        x_0 = np.ma.masked_equal(np.zeros([self.Xdep.Veld.shape[0], 1]), 0)
        xdep_vel = np.ma.vstack([y_0, xdep_vel])
        xdep_vel = np.ma.hstack([x_0, xdep_vel])
        ydep_vel = np.ma.vstack([y_0, ydep_vel])
        ydep_vel = np.ma.hstack([x_0, ydep_vel])
        return xdep_vel, ydep_vel

    def return_xyflat(self):
        """
        Output:
            Array met kolom x en kolom y-coordinaten, met cellen met nan waarden eruit gefilterd
        """
        xflat = self.Xdep.Veld.flatten()
        yflat = self.Ydep.Veld.flatten()
        xyflat = np.vstack((xflat, yflat)).T
        return xyflat

    def plot_rooster(self, *args, **kwargs):
        """ Plot lijnen rooster.

        Output:
            lijnen in Figuur-as
        """
        #kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, self.Xdep.Veld, self.Ydep.Veld)

        pyl.plot(self.Xdep.Veld, self.Ydep.Veld, *args, **kwargs)
        pyl.plot(self.Xdep.Veld.T, self.Ydep.Veld.T, *args, **kwargs)


class Sepveld(_BasisVeldPlot):
    """ functies speciaal voor data op waterstandspunten, zoals waterstand en constituent

    input:
                a) 1 argument => [numpy masked array]
                b) 2 argument => a)filenaam[string], b)pad[string]
                c) 3 arg, => 1)filenaam[string], 2)pad[string] , 3)filetype
                   opties filetype => [string=>'box'|'matfile']
    """
    def __init__(self, *arg):
        #from inl_waqua import veld as inl
        #veld = eval('inl().'+filetype+'(\''+vfile+'\', \''+vpad+'\')')
        #self._ini_veldobj(veld)
        _BasisVeldFunc.__init__(self, *arg)
        #self._ini_veldobj(*arg)
        #from mask_waquaveld import mask_zeta_value, mask_zeta_masker
        from mask_staggerdveld import mask_zeta_value, mask_zeta_masker
        self.return_plotmask = mask_zeta_masker
        self.return_valuemask = mask_zeta_value


    def pcolor(self, xbase=None, ybase=None, ax_h=None, colorbar=True, *args, **kwargs):
        if xbase is not None:
            print(xbase)
            #plot veld zonder xy- coordinaten
            xplot, yplot = self._return_xyplot(xbase, ybase)
        cb_handle = self._pcolor(xbase, ybase, ax_h, colorbar, *args, **kwargs)
        return cb_handle


    def pcolor_new(self, xbase=None, ybase=None, ax_h=None, colorbar=True, *args, **kwargs):
        if xbase is not None:
            #plot veld zonder xy- coordinaten
            xplot, yplot,xymasker = self._return_xyplot(xbase, ybase)
            xplot=np.ma.array(xplot,mask=xymasker)
            yplot=np.ma.array(yplot,mask=xymasker)
            print('xymasker')
            print(xymasker)
        else:
            xplot = xbase
            yplot = ybase
        print(xplot)
        #self._pcolor_new(xplot, yplot, ax, colorbar, *args, **kwargs)
        #try:   
        
        cb_handle = self._pcolor_new(xplot, yplot, xymasker, ax_h, colorbar, *args, **kwargs)
        #axlim = self._return_xylim(xbase, ybase)
        axlim = self._return_xylim(xplot, yplot)
        pyl.axis(axlim)#axlim = self._return_xylim(xplot, yplot)
        return cb_handle

    def pcolor_old(self, xbase=None, ybase=None, ax_h=None, colorbar=True, *args, **kwargs):
        if xbase is not None:
            #plot veld zonder xy- coordinaten
            xplot, yplot = self._return_xyplot(xbase, ybase)
            
            
        else:
            xplot = xbase
            yplot = ybase
        #self._pcolor_new(xplot, yplot, ax, colorbar, *args, **kwargs)
        
        print(xplot)
        cb_handle = self._pcolor_old(xplot, yplot, ax_h, colorbar, *args, **kwargs)
        return cb_handle

    def return_wat2dep(self):
        #if np.isnan(self.Veld).sum() == 0:
        #    print('Warning: nog even een tussenoplossing')
        #    sep = np.ma.masked_equal(self.Veld, 0)
        dep = self._return_veldaverage()
        y_0 = np.ma.masked_equal(np.zeros([1, dep.shape[1]]), 0)
        dep = np.ma.vstack([dep, y_0])
        x_0 = np.ma.masked_equal(np.zeros([dep.shape[0], 1]), 0)
        dep = np.ma.hstack([dep, x_0])
        return dep

    """
    def _return_xyplot(self, xbase, ybase):
        #from waqua_veld import Depveld, Rgfveld, Sepveld
        if isinstance(xbase, np.ma.MaskedArray):
            assert isinstance(ybase, np.ma.MaskedArray), \
                    'xbase en ybase zijn niet zelfde type! xbase = '\
                    +type(xbase)+', ybase = '+type(ybase)
            xplot = xbase
            yplot = ybase

        else:
            xclassname = xbase.__class__.__name__()
            yclassname = ybase.__class__.__name__()

            #if isinstance(xbase, Depveld):
            if xclassname == 'Depveld':
                assert xclassname == yclassname, \
                    'xbase en ybase zijn niet zelfde type! xbase = '\
                    +type(xbase)+', ybase = '+type(ybase)
                xplot = xbase.Veld
                yplot = ybase.Veld
            elif xclassname == 'Sepveld':#elif isinstance(xbase, Sepveld):
                assert xclassname == yclassname, \
                    'xbase en ybase zijn niet zelfde type! xbase = '\
                    +type(xbase)+', ybase = '+type(ybase)
                xplot = xbase.wat2dep()
                yplot = ybase.wat2dep()
            elif isinstance(xbase, Rgfveld):
                xplot = xbase.Xdep.Veld
                yplot = xbase.Ydep.Veld
        return xplot, yplot
    """
 
class Uveld(Sepveld):
    """ class U of V op WATERSTANDSPUNT!"""
    #def __init__(self, vfile, vpad, filetype):
    def __init__(self, *arg):
        print('nieuwe class maken uit "Veld" dictionary afkomstig van inl_waqua')
        #from inl_waqua import veld as inl
        #from mask_waquaveld import mask_zeta_value, mask_zeta_masker
        #from mask_staggerdveld import mask_zeta_value, mask_zeta_masker
        #arg = (vfile, vpad, filetype)
        print(arg)
        _BasisVeldFunc.__init__(self, *arg)
        #self._ini_veldobj(arg)

    def __add__(self, uveldobj):
        from waqua_veld import Velveld
        print('Maak stroomsnelheid-object op waterstandspunt uit U en V snelheid')
        #assert isinstance(uveldobj, wgtk.Uveld), 'Gebruik UVeld-object!'
        assert isinstance(uveldobj, self.__class__), 'Gebruik UVeld-object!'
        #check of velden verschillend zijn!
        diffuv = self.Veld-uveldobj.Veld
        assert np.nanmax(np.abs(diffuv)) > 0, 'U en V snelheid zijn identiek, check je invoer!'
        return Velveld(self, uveldobj)
        #return self.__init__(self, uveldobj)
        #def return_u2wat(self):
        #    wat = np.ma.masked_equal(self.Veld, 0)
        #    wat1 = u[0:-1, :]
        #    wat2 = u[1:, :]
        #    wat = (wat1+wat2)/2
        #    y = np.ma.masked_equal(np.zeros([1, dep.shape[1]]), 0)
        #    wat = np.ma.vstack([y, wat])
        #    return wat


#class Velveld(_BasisVeldPlot,Sepveld,Uveld):
class Velveld(Uveld):
    """ Class combi U en V  op waterstandspunt"""
    def __init__(self, veldU, veldV):
        import vector
        #from waquagrid_toolkit import Sepveld, Uveld
        print('grrrrrrrrrrrrr')
        assert isinstance(veldU, veldV.__class__)
        #from mask_waquaveld import mask_zeta_value, mask_zeta_masker
        from mask_staggerdveld import mask_zeta_value, mask_zeta_masker

        if isinstance(veldV, np.ndarray):
            veldV = np.ma.MaskedArray(veldV)
            veldU = np.ma.MaskedArray(veldU)

        if isinstance(veldU, np.ma.MaskedArray):
            self.U = Uveld(veldU)
            self.V = Uveld(veldV)
        elif isinstance(veldU, (Sepveld, Uveld)):
            self.U = veldU
            self.V = veldV
        else:
            raise TypeError
        vel = vector.Cart(self.U.Veld, self.V.Veld).cart2naut()
        self.Veld = vel[0]
        self.Veldcart2naut = vector.Cart(self.U.Veld, self.V.Veld).cart2naut()
        self.return_plotmask = mask_zeta_masker
        self.return_valuemask = mask_zeta_value

    def __sub__(self, velveldobj):
        #print(dir(self))
        #return wgtk.Sepveld(self.Veld-velveldobj.Veld)
        return Uveld(self.Veld-velveldobj.Veld)

    def quiver(self, xveld=None, yveld=None,
               mmin=1, mmax=None, nmin=1, nmax=None, mnint=1, *args, **kwargs):
        """Quiver plot
        Input:
            X= x-coordinaten, [None of np.ndarray ter grootte van model]
            Y= y-coordinaten, [None of np.ndarray ter grootte van model]
            mmin= minimum m-coordinaat [integer]
            nmin= minimum n-coordinaat [integer]
            mmax= maximum m-coordinaat [integer]
            nmax= maximum n-coordinaat [integer]
            mnint= slice- interval [interval
            *args = argumenten quiver
            **kwargs = argumenten quiver
        Output:
            x en y op waarde op waterstandpunt: 2*masked array
        """
        #kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, xveld, yveld)
        vmmax, vnmax = self.Veld.shape
        if mmax is None or mmax > self.Veld.shape[0]:
            mmax = vmmax-1
        if nmax is None or nmax > self.Veld.shape[1]:
            nmax = vnmax-1
        uquiv = self.U.Veld[mmin:mmax:mnint, nmin:nmax:mnint]
        vquiv = self.V.Veld[mmin:mmax:mnint, nmin:nmax:mnint]
        assert uquiv.compressed().size < 40000, 'Te veel punten geselecteerd.'
        if xveld is None and yveld is None:
            #Q = pyl.quiver(uquiv, vquiv)
            quiverveld = pyl.quiver(uquiv, vquiv, \
                scale_units='xy', units='width', \
                headwidth=8, headlength=3.5, headaxislength=2.5, \
                *args, **kwargs)
        else:
            try:
                #print(mmin, mmax, nmin, nmax)
                xquiv = xveld[mmin:mmax:mnint, nmin:nmax:mnint]
                yquiv = yveld[mmin:mmax:mnint, nmin:nmax:mnint]
            except IndexError:
                print(self.U.Veld.shape, self.V.Veld.shape, xveld.shape, yveld.shape)
                xquiv = xveld[mmin:mmax-1:mnint, nmin:nmax-1:mnint]
                yquiv = yveld[mmin:mmax-1:mnint, nmin:nmax-1:mnint]
            scaling = pt.SvaQuiver().quiverscaling(xquiv, yquiv, uquiv, vquiv)
            quiverveld = pyl.quiver(xquiv, yquiv, uquiv, vquiv, \
                scale=scaling, scale_units='xy', units='width', \
                headwidth=8, headlength=3.5, headaxislength=2.5, \
                *args, **kwargs)
        qkey = pt.SvaQuiver().quiverkey_current(quiverveld)
        return quiverveld, qkey


