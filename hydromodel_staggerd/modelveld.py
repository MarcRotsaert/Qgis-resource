import os
import numpy as np
#import pylab as pyl
import matplotlib.pyplot as pyl
import plottools as pt
#from waquagrid_toolkit import _handling_axeskwargs, list_methods
#from handling_kwargs import _handling_axeskwargs, list_methods
#import waquagrid_toolkit as wgtk
import mask_staggerdveld as msv

def list_methods(obj):
    """
    return lijst van methodes in object
    """
    methods = [method for method in dir(obj) if callable(getattr(obj, method))]
    if methods.count('__init__'):
        methods.remove('__init__')
    return methods

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

class _BasisVeldFunc(object):
    """ Verzameling functies die gerelateerd zijn aan het verwerken van de class-attribuut: Veld

    Subclass:
        .veldstatindex: veldstatistiek

    Attributen:
        - .Veld: velddata [numpy masked array]
        - .mask_ori: is originele masker aangepast  [bool]
        - .maskvalue: is originele masker aangepast met waarde [bool]
        - .maskenclosure: is originele masker aangepast op _Basis van enclosure[bool]
        - .maskindex  is originele masker aangepast op _Basis van index
    """
    def __init__(self, *arg):
        """1) Attribuut Veld toevoegen aan object
           2) MaskVeld, MaskValue, MaskEnclosure en MaskIndex toevoegen aan object
        Input:
            - arg=
                a) 1 argument => [numpy array]
                a) 2 argument => a)filenaam[string], b)pad[string]
                b) 3 argumenten = > a)filenaam[string], b)pad[string], c)filetype[string]
        Output:
            Instance Veld-object
        Afhankelijkheid binnen module:
            nvt
        """
        from inl_waqua import veld as inl

        print(len(arg))
        assertstring = r"initieer met 1invoerparameter(numpy array?),2  of \
        3 invoerparameters \
            (1) filenaam, \
            (2) pad, \
            (3) filetype\n" #len(arg) = "+ str(arg) + r", type(arg[0] = "+str(arg[0])
        assert 0 < len(arg) < 4, assertstring

        if len(arg) == 1:
            assert issubclass(type(arg[0]), np.ndarray)
            veld = arg[0]
        else:
            vfile = arg[0]
            vpad = arg[1]
            vpad = vpad.replace('\\', '/')
            if len(arg) == 2:
                print(arg)
                if len(arg[0].split('mat')) == 2:
                    #filetype = 'getdatamat'
                    filetype = inl().getdatamat
                else:
                    filetype = inl().box
            else:#len(arg) == 3:
                if arg[2] == 'getdatamat':
                    filetype = inl().getdatamat
                else:
                    filetype = inl().box
            #assert list_methods(inl).count(filetype) == 1, \
            #    "filetype onbekend bestandsformaat"
            #assert filetype != 'rgf', "gebruik class Rgfveld ipv Depveld"
            #evalline = 'inl().'+filetype+'(\''+vfile+ '\', '+'\''+vpad+'\')'
            #print(evalline)
            #veld = eval(evalline)
            veld = filetype(vfile, vpad)
            print('attribuut "Veld" afkomstig van inl_waqua')

        self.maskveld = False
        self.maskvalue = False
        self.maskenclosure = False
        self.maskindex = False

        if isinstance(veld, np.ndarray):
            masker = np.zeros(veld.shape, dtype=bool)
            veld = np.ma.MaskedArray(veld, mask=masker)
            #veld.mask = masker
        self.Veld = veld
        self.mask_ori = self.Veld.mask.copy()
        from info_waquaveld import veldstatistiek
        self.veldstatindex = veldstatistiek.index(veld)

    def __add__(self, addobj):
        #import waquagrid_toolkit as wgtk
        try:
            diffveld = self.Veld.copy()+addobj
        except TypeError:
            assert self.__class__.__name__ == addobj.__class__.__name__
            diffveld = self.Veld.copy().addobj.Veld
        diffobj = eval('wgtk.'+self.__class__.__name__+'(diffveld)')
        return diffobj

    def __getitem__(self, slice):
        """
        Slicing laten werken op attribuut Veld.
        """
        return self.Veld[slice]


    def set_maskori(self):
        """Reset van mask voor veld attribuut

        Input:
            None
        Output:
            Reset attribuut Veld
        Afhankelijkheid binnen module:
            nvt
        """
        self.Veld = np.ma.masked_array(self.Veld, mask=self.mask_ori)
        self.maskveld = False
        self.maskvalue = False
        self.maskenclosure = False
        self.maskindex = False

    def set_maskveld(self, maskveld, invert=False):
        """Leg nieuw mask  op voor veld attribuut

        Input:
            - maskveld= Veld waarmee mask aangepast wordt[numpy maskedarray |numpy array .boolean]
            - invert = keer het op te leggen masker om [bool]
        Output:
            Aanpassing attribuut Veld

        Afhankelijkheid binnen module:
            nvt
        """
        #pyl.figure();pyl.pcolormesh(maskveld.mask)
        assert(maskveld.shape == self.Veld.shape), \
            'mask veld moet zelfde afmetingen hebben als masked array.'
        if isinstance(maskveld, np.ma.MaskedArray):
            masker = maskveld.mask
        elif maskveld.dtype == bool:
            masker = maskveld
        #if invert == True:
        if invert:
            masker = np.invert(masker)
        self.Veld = np.ma.masked_array(self.Veld, mask=masker)

        self.maskveld = True
        self.maskvalue = False
        self.maskenclosure = False
        self.maskindex = False

    def set_maskindex(self, index):
        """Verander masker op _Basis van index voor Veld attribuut

        Input:
            - index= iterable indexnnummers, [ bijv. list, numpy array]
        Output:
            Aanpassing attribuut Veld
        Afhankelijkheid binnen module:
            nvt
        """
        mask = self.Veld.mask #return mask
        mask[index[:, 0], index[:, 1]] = True
        self.Veld = np.ma.masked_array(self.Veld, mask=mask)
        self.maskveld = False
        self.maskvalue = False
        self.maskenclosure = False
        self.maskindex = True

    def set_maskenclosure(self, enclosure):
        """Verander masker op _Basis van enclosure voor Veld attribuut

        Input:
            enclosure= Iterable met path (bijvoorbeeld object gemaakt met inl_waqua.route.enclosure)
        Output:
            Aanpassing attribuut Veld
            Update .mask_ori
            Update veldstatindex
        Afhankelijkheid binnen module:
            nvt
        """
        mveld, nveld = self.return_mnveld()
        mnveld_flat = np.array([mveld.flatten(), nveld.flatten()]).T
        masker = np.zeros(mveld.size)
        tempmasker = np.zeros(mveld.size)
        tel = 1
        for encl in enclosure.path:
            print('Set mask enclosure lijnstuk: '+str(tel))
            p_in = encl.contains_points(mnveld_flat)
            tempmasker = tempmasker+p_in
            print(u'\t'+str(sum(tempmasker))+' punten in lijn '+str(tel))
            tel = tel+1
        tempmasker = tempmasker.reshape(mveld.shape)
        masker = tempmasker != 1
        self.Veld = np.ma.masked_array(self.Veld, mask=masker)
        self.mask_ori = np.logical_or(self.mask_ori, masker)
        self.maskveld = False
        self.maskvalue = False
        self.maskenclosure = True
        self.maskindex = False
        if hasattr(self, 'veldstatistiek'):
            del self.veldstatindex
            from info_waquaveld import veldstatistiek
            self.veldstatindex = veldstatistiek.index(self.Veld)
        #BELANGRIJK: NA ENCLOSURE WORDT OOK HET OORSPRONKELIJKE Masker AANGEPAST
        return masker

    def set_maskvalue(self, value, operator='='):
        """Verander masker op _Basis van overschrijding/onderschrijding/overeenkomende waarde
        Input:
            - value= waarde[numeric]
            - operator = ['='|'<'|'>']
        Output:
            Aanpassing attribuut Veld
        Afhankelijkheid binnen module:
            nvt
        """
        print(type(value))
        veldproc =np.nan_to_num(self.Veld)
        
        if operator in ['=', '>', '<']:
            if operator == '=':
                veldproc =np.nan_to_num(self.Veld,nan=value+1)
                #tempveld = self.Veld.filled(value)
                mask_val = value == veldproc
                #mask_val = value == self.Veld.data
                            #self.Veld = np.ma.masked_equal(self.Veld.data, value)
                #temp = np.ma.masked_equal(self.Veld.data, value)
                #mask_val = temp.mask
                #masker = np.logical_or(self.mask_ori, mask_val)
                            #self.Veld.mask = np.logical_or(self.mask_ori, mask_val)
            elif operator == '<':
                veldproc =np.nan_to_num(self.Veld,nan=value+1)
                #tempveld = self.Veld.filled(value+1)
                #tempveld = self.Veld.filled(value)
                mask_val = value < veldproc
                #mask_val = value<self.Veld.data
                #self.Veld = np.ma.masked_greater(self.Veld.data, value)
                #masker = np.logical_or(self.mask_ori, mask_val)
                            #self.Veld.mask = np.logical_or(self.mask_ori, mask_val)
            elif operator == '>':
                veldproc = np.nan_to_num(self.Veld,nan=value-1)
                #tempveld = self.Veld.filled(value-1)
                #tempveld = self.Veld.filled(value)
                mask_val = value > veldproc
                #mask_val = value>self.Veld.data
                #print(mask_val)
                #print(value)
                #print(self.Veld.data)
                            #self.Veld = np.ma.masked_less(self.Veld.data, value)
            masker = np.logical_or(self.mask_ori, mask_val)
        else:
            raise TypeError( \
                'Foute invoer: operator = ' +str(operator)+'value = '+str(value))
        #pyl.pcolormesh(mask_val)

        self.Veld.mask = masker
        self.maskvalue = True
        self.maskveld = False
        self.maskenclosure = False
        self.maskindex = False

        if hasattr(self, 'veldstatindex'):
            del self.veldstatindex
            from info_waquaveld import veldstatistiek
            self.veldstatindex = veldstatistiek.index(self.Veld)
        return mask_val

    def set_datavalue_nan2num(self, value=None):
        """    vervang nanwaarden door andere waarde
        Input:
            value= None | waarde
                indien None: nan wordt vervangen door 0 of inf
                indien waarde: nan wordt vervangen door waarde of inf
        Output:
            - Aanpassing attribuut Veld
        """
        if value is None:
            self.Veld = np.nan_to_num(self.Veld.copy)
        else:
            raise NotImplementedError

    def set_datavalue_extra(self, value_ori, value_new, operator='='):
        """    vervang cellen door andere waarde , extra optie =<>
            - '<'=> vervang alle waarden Kleiner dan\n
            - '>'=> vervang alle waarden Groter dan\n
            - '='=> vervang alle waarden Gelijk aan\n
        Input:
            - value_ori= waarde[numeric]
            - value_new= waarde [numeric]
            - operator=['='|'<'|'>']
        Output:
            - Aanpassing attribuut Veld
            - Update .mask_ori
            - return veld
        Afhankelijkheid binnen module:
            nvt
        """
        ori_shape = self.Veld.shape
        veld_flat = self.Veld.copy().flatten()
        if operator == '=':
            i = np.where(veld_flat == value_ori)
                #self.Veld.data = np.ma.masked_equal(self.Veld.data, value)
        elif operator == '>':
            i = np.where(veld_flat > value_ori)
        elif operator == '<':
            i = np.where(veld_flat < value_ori)
        veld_flat[i] = value_new
        veld_flat = np.reshape(veld_flat, ori_shape)
        self.Veld.data[:] = veld_flat[:]
        del self.veldstatindex
        from info_waquaveld import veldstatistiek
        self.veldstatindex = veldstatistiek.index(self.Veld)

        return self.Veld.data

    def return_mnveld(self):
        """return 2 velden analoog met het self.Veld met nummering  m en n

        Input:
            - None
        Output:
            - veld met m-coordinaten, met dimensies overeenkomend self.Veld  [numpy array]
            - veld met n-coordinaten, met dimensies overeenkomend self.Veld [numpy array]
        Afhankelijkheid binnen module:
            nvt
        """
        mlen, nlen = self.Veld.shape
        mveld = np.array([range(1, mlen+1)]*nlen, dtype='i').T

        nveld = np.array([range(1, nlen+1)]*mlen, dtype='i')
        return mveld, nveld

    def return_mncompressed(self):
        """return 2 velden met nummering  m en n, van cellen zonder mask.
        Input:
            None
        Output:
            - veld met m-coordinaten, met dimensie 1*X  [numpy array]
            - veld met n-coordinaten, met dimensies 1*X [numpy array]
        Afhankelijkheid binnen module:
            nvt
        """

        mask = self.Veld.mask
        #mlen, nlen = self.Veld.shape
        mveld, nveld = self.return_mnveld()
        mveld = np.ma.array(mveld, mask=mask)
        nveld = np.ma.array(nveld, mask=mask)
        ncompressed = np.ma.compressed(nveld)
        mcompressed = np.ma.compressed(mveld)
        return mcompressed, ncompressed

    def return_veldcompressed(self):
        """return veld van cellen zonder mask.

        Output:
            veld met waarden uit self.Veld, met dimensie 1*X  [numpy array]
        Afhankelijkheid binnen module:
            nvt
        """
        veldcompressed = np.ma.compressed(self.Veld)
        return veldcompressed

    def _return_veldaverage(self):
        """return gemiddelde vier omliggende punten  van een veld.
        Output:
            veld met waarden uit self.Veld, met dimensie 1*X  [numpy array]
        Afhankelijkheid binnen module:
            nvt
        """
        veld = np.ma.masked_equal(self.Veld, 0)
        average1 = veld[0:-1, 0:-1]
        average2 = veld[1:, 1:]
        average3 = veld[0:-1, 1:]
        average4 = veld[1:, 0:-1]
        average = (average1+average2+average3+average4)/4
        return average

    def make_boxfile(self, bfile, bpad, dummy=-10, layer=0):
        """Maak boxfile uit attribuut Veld.
        Input:
            - bfile = naam boxfile [string]
            - bpad = pad boxfile [string]
            - dummy = dummy waarde [float]
        Output:
            File in bestandsformaat Box [Ascii]
        Afhankelijkheid binnen module:
            nvt
        """
        step = 10
        fhandle = open(os.path.join(bpad, bfile), 'w')
        mmax, nmax = self.Veld.shape
        indexstrook = range(0, nmax+step, 10)
        if indexstrook[-1]-1 > nmax:
            indexstrook[-1] = nmax
        teller = len(indexstrook)-1
        m1 = 0
        self.Veld.set_fill_value(dummy)
        mat = self.Veld.filled()
        mat = np.nan_to_num(mat)
        for i in range(0, teller-1):
            if layer == 0:
                string = 'BOX MNMN = ({:4d}, {:4d}, {:4d}, {:4d}) VARIAble_values = \n'\
                    .format(m1+1, indexstrook[i]+1, mmax, indexstrook[i+1])
            else:
                string = \
                'BOX MNMN = ({:4d}, {:4d}, {:4d}, {:4d}), Layer = {:2d}, VARIAble_values = \n'\
                .format(m1+1, indexstrook[i]+1, mmax, indexstrook[i+1], layer)
            fhandle.write(string)
            for j in range(m1, mmax):
                rij = mat[j, range(indexstrook[i], indexstrook[i+1]+1)]
                formatter = ''
                formatter = (len(rij)-1)*'{: 9.3f}'+'\n'
                #for i2 in range(1, len(rij)):
                #    formatter = formatter+'{: 9.3f}'
                #formatter = formatter+'\n'
                string = formatter.format(*rij)
                fhandle.write(string)
        #Laatste n-rij
        i = i+1
        string = 'BOX MNMN = ({:4d}, {:4d}, {:4d}, {:4d}) VARIAble_values = \n'.\
            format(m1+1, indexstrook[i]+1, mmax, indexstrook[i+1])
        fhandle.write(string)
        for j in range(m1, mmax):
            rij = mat[j, range(indexstrook[i], indexstrook[i+1])]
            formatter = ''
            formatter = len(rij)*'{: 9.3f}'+'\n'
            #for i2 in range(1, len(rij)+1):
            #    formatter = formatter+'{: 9.3f}'
            #formatter = formatter+'\n'
            string = formatter.format(*rij)
            fhandle.write(string)
        fhandle.close()


class _BasisVeldPlot(_BasisVeldFunc):
    def __init__(self):
        self.Veld = np.array([])
        self.mask_value = np.array([])
    def _return_plotveld_origineel(self, maskveld, nanvalue=None):
        """Return uit class-attribuut Veld de variabele plotveld.
        Dit veld kan direct met pcolormesh geplot kan worden.
        Input:
            - maskveld = array met afmetingen m en n         [numpy masked array]
            - nanvalue = numeric        [int|float]
        Output:
            array met afmetingen m en n [numpy masked array]
        Afhankelijkheid binnen module:
            - self.return_plotmask
            - self.mask_value
    """
        assert(isinstance(maskveld, np.ma.MaskedArray)), 'maskveld moet masked array zijn!'
        if nanvalue is None:
            mask = self.return_plotmask(self.Veld, maskveld)
        else:
            mask = self.mask_value(maskveld, nanvalue)

        mask = mask is False
        plotveld = np.ma.masked_array(self.Veld, mask=mask)
        return plotveld

    def _return_plotveld(self,xyveld):
        import mask_staggerdveld as msv
        plotveld = self.Veld.copy()
        plotveld[plotveld == 0] = np.nan
        plotveld.mask
        selfclassname = self.__class__.__name__
        #print(self.Veld.mask)
        #print(xyveld.shape)
        #print(xyveld)
        if selfclassname == 'Depveld':
            #masker = msv.mask_dep_masker(DPD.Veld,RGF.return_dep2wat()[0])
            #xymasker = msv.mask_dep_masker(self.Veld,xyveld)
            xymasker = msv.mask_dep_masker(self.Veld,xyveld)

        elif selfclassname == 'Sepveld':
            #masker = msv.mask_dep_masker(WL.Veld,Rgf.Xdep.Veld)
            xymasker = msv.mask_dep_masker(self.Veld,xyveld)    
        #self.set_maskveld(masker.mask)
        #print(xymasker)
        masker = plotveld.mask+xymasker
       
        plotveld = np.ma.array(plotveld,mask=masker.mask)
        return plotveld

    def _return_xyplot(self, xbase, ybase):
        print(type(xbase))
        #assert isinstance(xbase,(np.ma.MaskedArray, wgtk.Depveld, wgtk.Sepveld, wgtk.Rgfveld))
        print(isinstance(xbase, np.ma.MaskedArray))
        xymasker = None
        print('xbase')
        print(type(xbase))
        print(isinstance(xbase, np.ma.MaskedArray))
        if isinstance(xbase, np.ma.MaskedArray):
            assert isinstance(ybase, np.ma.MaskedArray), \
                    'xbase en ybase zijn niet zelfde type! xbase = '\
                    +type(xbase)+', ybase = '+type(ybase)
            xplot = xbase
            yplot = ybase
            xymasker = xplot.mask
        else:
            xclassname = xbase.__class__.__name__
            yclassname = ybase.__class__.__name__
            selfclassname = self.__class__.__name__
            if selfclassname == 'Depveld':
                if xclassname == 'Rgfveld':#if isinstance(xbase, wgtk.Rgfveld):
                    xplot, yplot = xbase.return_dep2wat()
                    xymasker = xplot.mask.copy()
                    
                elif xclassname == 'Depveld': #elif isinstance(xbase, wgtk.Depveld):
                    #assert isinstance(ybase, wgtk.Depveld), \
                    #    'xbase en ybase zijn niet zelfde type! xbase = '\
                    #+type(xbase)+', ybase = '+type(ybase)
                    assert xclassname == yclassname, \
                        'xbase en ybase zijn niet zelfde type! xbase = '\
                        +type(xbase)+', ybase = '+type(ybase)

                    xplot = xbase.return_dep2wat()
                    yplot = ybase.return_dep2wat()
                    xymasker = xplot.mask.copy()
                    #veld= self.return_plotveld(xplot)
                elif xclassname == 'Sepveld':#elif isinstance(xbase, Sepveld):
                    #assert isinstance(ybase, wgtk.Sepveld), \
                    #    'xbase en ybase zijn niet zelfde type! xbase = '\
                    #+type(xbase)+', ybase = '+type(ybase)
                    assert xclassname == yclassname, \
                        'xbase en ybase zijn niet zelfde type! xbase = '\
                        +type(xbase)+', ybase = '+type(ybase)
                    xplot = xbase.Veld
                    yplot = ybase.Veld
                    xymasker = xbase.Veld.mask.copy()
                else:
                    raise Exception( 'Ongeldig invoer voor X')
            elif selfclassname == 'Sepveld':  #elif (self, wgtk.Sepveld):
                if xclassname == 'Rgfveld':#if isinstance(xbase, wgtk.Rgfveld):
                    xplot = xbase.Xdep.Veld
                    yplot = xbase.Ydep.Veld
                    xymasker = xbase.Xdep.Veld.mask.copy()
                elif xclassname == 'Depveld':#elif isinstance(xbase, wgtk.Depveld):
                    #assert isinstance(ybase, wgtk.Depveld), \
                    #    'xbase en ybase zijn niet zelfde type! xbase = '\
                    #+type(xbase)+', ybase = '+type(ybase)
                    assert xclassname == yclassname, \
                        'xbase en ybase zijn niet zelfde type! xbase = '\
                        +type(xbase)+', ybase = '+type(ybase)
                    xplot = xbase.Veld
                    yplot = ybase.Veld
                    xymasker = xbase.Veld.mask.copy()
                elif xclassname == 'Sepveld':#elif isinstance(xbase, wgtk.Sepveld):
                    #assert isinstance(ybase, wgtk.Sepveld), \
                    #    'xbase en ybase zijn niet zelfde type! xbase = '\
                    #+type(xbase)+', ybase = '+type(ybase)
                    assert xclassname == yclassname, \
                        'xbase en ybase zijn niet zelfde type! xbase = '\
                        +type(xbase)+', ybase = '+type(ybase)
                    xplot = xbase.wat2dep()
                    yplot = ybase.wat2dep()
                    xymasker = xplot.Veld.mask.copy()
        xplot=np.nan_to_num(xplot.data)
        
        yplot=np.nan_to_num(yplot.data)
            #else:
            #   raise NotImplementedError, 'Nog niet geimplementeerd............. '
        return xplot, yplot,xymasker



        def _pcolor_axislim(xplot,yplot):
            xdump=np.ma.xplot(mask=xplot>1e30)
            ydump=np.ma.yplot(mask=yplot>1e30)
            return [np.ma.min(xdump),np.ma.max(xdump),np.ma.min(ydump),np.ma.max(ydump)]

    def _pcolor_setcol(self, lim, nr_klasse, xplot=None, yplot=None, xymasker=None,ax=None, *args, **kwargs):
        kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, xplot, yplot)
        maskerveld = np.ma.array(xplot,mask=xymasker)
        print('yes')
        print(maskerveld)
        veld = self._return_plotveld(maskerveld)
        self._pcolor_new(xplot, yplot, colorbar=False, *args, **kwargs)
        #pt.SvaColormap().set_Normpcolor(ax, lim, nr_klasse)
        pt.SvaColormap().set_Normpcolor(kwargs['axes'], lim, nr_klasse)
        #if colorbar:
        pt.SvaAxis(kwargs['axes']).axisequal()
        return pyl.colorbar()


    def _pcolor_new(self, xplot=None, yplot=None, xymasker=None, ax=None, colorbar=True, *args, **kwargs):
        """ Gemaksfunctie voor plotten veld.
        Input:
            - x => None of object dat Veld met coordinaten  voorstelt \
                [wgtk.Rgfveld|wgtk.Depveld|wgtk.Sepveld|numpy masked array]
            - y => None of object dat Veld met coordinaten voorstelt
            - ax => handle naar as [matplotlib.axes._subplots.AxesSubplot]
            - colorbar => al dan niet colorbar  [bool]
            - *args, **kwargs => argumenten uit matplotlib.pyplot.pcolormesh
        Output:
            - plot van pcolormesh [zonder referentie]
            - Eventueel: Return handle naar colorbar [matplotlib.pyplot.colorbar]
        Afhankelijkheid:
            self.return_plotveld
        """

        kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, xplot, yplot)
        if xplot is None:
            #plot veld zonder xy- coordinaten
            pyl.pcolormesh(self.Veld.T, *args, **kwargs)
        else:
            #print(xymasker)
            #print(xplot)
            #xplot, yplot = self._return_xyplot(xplot, yplot)
            maskerveld = np.ma.array(xplot,mask=xymasker)
            veld = self._return_plotveld(maskerveld)
            if veld.shape[0] == xplot.shape[0]:
                it1 = None
            else:
                it1 = -1
                #it1 = None
            if veld.shape[1] == xplot.shape[1]:
                it2 = None
            else:
                it2 = -1
            #np.nan_to_num(xplot)
            #np.nan_to_num(yplot)
            
            #print(xplot)
            try:
                pyl.pcolormesh(xplot, yplot, veld, *args, **kwargs)
            except ValueError:
                pyl.pcolormesh(xplot.data, yplot.data, veld, *args, **kwargs)

            #print(xplot)
            #tempx = np.ma.array(xplot[0:it1, 0:it2],mask=self.Veld.mask)
            #tempy = np.ma.array(yplot[0:it1, 0:it2],mask=self.Veld.mask)
            #pyl.axis([np.nanmin(tempx), np.nanmax(tempx), np.nanmin(tempy), np.nanmax(tempy)])

             
            pyl.clim(np.nanmin(self.Veld), np.nanmax(self.Veld))
            #print(np.nanmax(veld))
            pt.SvaAxis(kwargs['axes']).axisequal()
        if colorbar:
            return pyl.colorbar()

    def _contourf(self, xplot=None, yplot=None, xymasker=None, nr_klasse=None, axes=None, colorbar=True, *args, **kwargs):
        """Gemaksfunctie voor plotten filled contour.
        Met automatisch aanpassen van x en y assen
        Voor Input, Output en afhankelijkheden binnen module.
            Zie: self.pcolor
        """
        kwargs.update({'axes':axes})
        veld = self.Veld
        kwargs = _handling_axeskwargs(kwargs, xplot, yplot)

        #lim = None
        lim = [np.nanmin(veld), np.nanmax(veld)]
        if nr_klasse is not None:
            norm = pt.SvaColormap().return_Norm(lim, nr_klasse)
            print(norm)
        else:
            norm = None
        kwargs.update({'norm':norm})
        
        if xplot is None:
            #pyl.contourf(veld, axes = ax, *args, **kwargs)
            pyl.contourf(veld, *args, **kwargs)
        else:
            #27-4-20
            maskerveld = np.ma.array(xplot,mask=xymasker)
            veld = self._return_plotveld(maskerveld)
            #27-4-20
            #xplot, yplot = self._return_xyplot(x, y)
            #print(kwargs.keys())
            pyl.contourf(xplot[0:veld.shape[0], 0:veld.shape[1]], \
                         yplot[0:veld.shape[0], 0:veld.shape[1]], veld, *args, **kwargs)
            print(kwargs)            
            pt.SvaAxis(kwargs['axes']).axisequal()
            #pyl.xlim(np.nanmin(xplot), np.nanmax(xplot))
            #pyl.ylim(np.nanmin(yplot), np.nanmax(yplot))
            if lim is not None:
                pyl.clim(lim)
                print('grr')
            else:
                pyl.clim(np.nanmin(veld), np.nanmax(veld))
        if colorbar:
            return pyl.colorbar() 
 
    def _pcolor_old(self, xplot=None, yplot=None, ax=None, colorbar=True, *args, **kwargs):
        """ Gemaksfunctie voor plotten veld.
        Input:
            - x => None of object dat Veld met coordinaten  voorstelt \
                [wgtk.Rgfveld|wgtk.Depveld|wgtk.Sepveld|numpy masked array]
            - y => None of object dat Veld met coordinaten voorstelt
            - ax => handle naar as [matplotlib.axes._subplots.AxesSubplot]
            - colorbar => al dan niet colorbar  [bool]
            - *args, **kwargs => argumenten uit matplotlib.pyplot.pcolormesh
        Output:
            - plot van pcolormesh [zonder referentie]
            - Eventueel: Return handle naar colorbar [matplotlib.pyplot.colorbar]
        Afhankelijkheid:
            self.return_plotveld
        """

        kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, xplot, yplot)
        if xplot is None:
            #plot veld zonder xy- coordinaten
            pyl.pcolormesh(self.Veld.T, *args, **kwargs)
        else:
            #xplot, yplot = self._return_xyplot(x, y)
            #if isinstance(xplot, np.ma.MaskedArray):
            #veld = self._return_plotveld()[1:, 1:]
            #veld = self._return_plotveld()
            #else: #if isinstance(self, wgtk.Depveld) or isinstance(self, wgtk.Sepveld):
            veld = self._return_plotveld()
            #else:
            #    else:
            #        raise NotImplementedError,\
            #        'Nog niet geimplementeerd voor anderen dan masked array'
            veld = veld.filled(np.nan)
            xplot = xplot.filled(np.nan)
            yplot = yplot.filled(np.nan)
            #xplot_ori = xplot.copy()
            if veld.shape[0] == xplot.shape[0]:
                it1 = None
            else:
                it1 = -1
            if veld.shape[1] == xplot.shape[1]:
                it2 = None
            else:
                it2 = -1
            tempx = xplot[0:it1, 0:it2]
            tempy = yplot[0:it1, 0:it2]
            vmask = self.Veld.mask.copy()
            tempx[vmask] = np.nan
            xplot[0:it1, 0:it2] = tempx
            #tempy[vmask.copy() == True] = np.nan
            tempy[vmask.copy()] = np.nan
            yplot[0:it1, 0:it2] = tempy
            pyl.pcolormesh(xplot, yplot, veld, *args, **kwargs)
            pyl.axis([np.nanmin(xplot), np.nanmax(xplot), np.nanmin(yplot), np.nanmax(yplot)])
        pyl.clim(np.nanmin(self.Veld), np.nanmax(self.Veld))
        pt.SvaAxis(kwargs['axes']).axisequal()
        if colorbar:
            return pyl.colorbar()




    def _pcolor(self, xplot=None, yplot=None, ax=None, colorbar=True, *args, **kwargs):
        from waqua_veld import Depveld, Rgfveld, Sepveld
        """ Gemaksfunctie voor plotten veld.
        Input:
            - x => None of object dat Veld met coordinaten  voorstelt \
                [wgtk.Rgfveld|wgtk.Depveld|wgtk.Sepveld|numpy masked array]
            - y => None of object dat Veld met coordinaten voorstelt
            - ax => handle naar as [matplotlib.axes._subplots.AxesSubplot]
            - colorbar => al dan niet colorbar  [bool]
            - *args, **kwargs => argumenten uit matplotlib.pyplot.pcolormesh
        Output:
            - plot van pcolormesh [zonder referentie]
            - Eventueel: Return handle naar colorbar [matplotlib.pyplot.colorbar]
        Afhankelijkheid:
            self._return_plotveld
        """

        print('Oude methode voor plotten velden')
        kwargs.update({'axes':ax})
        kwargs = _handling_axeskwargs(kwargs, xplot, yplot)
        if xplot is None:
            #plot veld zonder xy- coordinaten
            pyl.pcolormesh(self.Veld.T, *args, **kwargs)
        else:
            veld = self._return_plotveld_origineel(xplot)
            pyl.pcolormesh(xplot.data, yplot.data, veld, *args, **kwargs)
            axlim =self._pcolor_axislim(xplot,yplot)
            pyl.axis([np.nanmin(xplot), np.nanmax(xplot), np.nanmin(yplot), np.nanmax(yplot)])
            pyl.clim(np.nanmin(self.Veld), np.nanmax(self.Veld))
        pt.SvaAxis(kwargs['axes']).axisequal()
        if colorbar:
            return pyl.colorbar()
    def _return_xylim(self,xplot,yplot):
        print(xplot)
        veld = self._return_plotveld(xplot)
        if veld.shape[0] == xplot.shape[0]:
            it1 = None
        elif veld.shape[0]+1==xplot.shape[0]:
            it1 = -1
        else:
            return [None, None, None, None]
        if veld.shape[1] == xplot.shape[1]:
            it2 = None
        elif veld.shape[1]+1==xplot.shape[1]:
            it2 = -1
        else:
            return [None, None, None, None]
        try:
            tempx = np.ma.array(xplot[0:it1, 0:it2],mask=self.Veld.mask)
            tempy = np.ma.array(yplot[0:it1, 0:it2],mask=self.Veld.mask)
            tempx1 = np.ma.array(xplot[1:, 1:],mask=self.Veld.mask)
            tempy1 = np.ma.array(yplot[1:, 1:],mask=self.Veld.mask)
            print([np.nanmin(tempx), np.nanmax(tempx), np.nanmin(tempy), np.nanmax(tempy)])
        except Exception as ex:
            print(ex)
            print(tempx.shape,tempy.shape)
            print(xplot.shape,yplot.shape)

        
        return [np.nanmin(tempx), np.nanmax(tempx), np.nanmin(tempy), np.nanmax(tempy)]
        #return tempx,tempy
        #return [np.nanmin(tempx), np.nanmax(tempx), np.nanmin(tempy), np.nanmax(tempy)]

    def plot_statistiek(self, stat=None, inputstat=None, xplot=None, yplot=None, *args, **kwargs):
        """    Plot in een kaartje index afkomstig uit veldstatistiek.

        Input:
            - stat= naam van functie [string]
            - inputstat= input parameters functie  [numeric | iterable]
            - xplot= veld met x-coordinaten [numpy array ]
            - yplot= veld met y-coordinaten [numpy array ]
            - ax = assenstelsel [handle naar assenstelsel]
            - *args = argumenten voor plot [list|tuple]
            - **kwargs = argumenten voor plot [dictionary]
        Output:
            kaartje gemaakt met pyplot.plot
        Afhankelijkheid binnen module:
            list_methods
        """
        if stat is None:
            print("\'stat\' opties:")
            print(list_methods(self.veldstatindex))
            return
        if inputstat is None:
            inp = ''
        else:
            if not isinstance(inputstat, list):
                inputstat = [inputstat]
            inp = ''
            for i in inputstat:
                inp = inp+str(i)+', '
        eval_string = 'self.veldstatindex.'+stat+'('+ inp+')'
        #print(eval_string)

        try:
            i = eval(eval_string)
        except (TypeError, SyntaxError):
            print('Error on:')
            print('\t'+eval_string)
            print('\tinput = '+str(inputstat))
            print('\tx = '+str(xplot))
            print('\ty = '+str(yplot))
            print('\tCorrect gebruik statistiek:')
            print('\t'+eval('help(self.veldstatindex.'+stat+')'))
            raise Exception
        #except:
        #    print(Argument)
            raise Exception
        if i.size > 2:
            m_i = i[:, 0]+1
            n_i = i[:, 1]+1
        else:
            m_i = i[0]+1
            n_i = i[1]+1
        if xplot is None:
            xyplot = [m_i, n_i]
            #xplot = m_i
            #yplot = n_i
            labels = ['m', 'n']
            #ylab = 'n'
            #xlab = 'm'
        else:
            xyplot = [xplot[m_i, n_i], yplot[m_i, n_i]]
            #xplot = x[m_i, n_i]
            #yplot = y[m_i, n_i]
            labels = ['x-coordinaten', 'y-coordinaten']
            #xlab = 'x-coordinaten'
            #ylab = 'y-coordinaten'
        pyl.plot(xyplot[0], xyplot[1], '*', *args, **kwargs)
        pyl.xlabel(labels[0])
        pyl.ylabel(labels[1])
        #pyl.plot(xplot, yplot, '*', *args, **kwargs)
        #pyl.xlabel(xlab)
        #pyl.ylabel(ylab)


#class _BasisVeld(_BasisVeldPlot):
    #"""Combinatie van _Basis plotfuncties  en _Basis veldfuncties"""
    #def __init__(self):
    #    self._BasisVeldFunc()
    #    self._BasisVeldPlot()
    #    print('start _Basis Veld')

