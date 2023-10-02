"""
Toolbox voor Waqua tijdsersies
"""
import os
import datetime
import numpy as np
import pylab as pyl

from waquagrid_toolkit import Punt
from inl_waqua import tijdreeks as inlw
#import waquaseries_toolkit as wstk

def decorate_write(func):
    def function_wrap(*args, **kwargs):
        func(*args, **kwargs)
        print(u"\u001b[48;5;" + str(11) + "m " + "ts regular weggegeschreven")

        print(os.path.join(args[2], args[1]) +    u'\u001b[0m')
    return function_wrap

def decorate_plot(func):
    def function_wrap(*args, **kwargs):
        func(*args, **kwargs)
        print(u"\u001b[42;1;" + str(11) + "m " + "plot Figure:")
        print(pyl.gcf().canvas.manager.get_window_title() +    u'\u001b[0m')
        #print(pyl.gcf().canvas.get_window_title() +    u'\u001b[0m')
    return function_wrap

class _FuncTs(object):
    def __init__(self):
        self._set_defaultattributen()

    def _copy_wstkattributen(self, attrdict):
        self.Punt = attrdict['Punt'].copy()
        self.Meta = attrdict['Meta'].copy()
        self.Data = []

        # for data in attrdict['Data']:
        #    selfobj.Data.append(data.copy())
        self.Data = attrdict['Data']
        #self.Tijd = attrdict['Tijd'].copy()
        self.Tijd = []
        for tijd1 in attrdict['Tijd']:
            self.Tijd.append(tijd1)
        self.Tijdmin = []
        for tijd in attrdict['Tijdmin']:
            self.Tijdmin.append(tijd)
        #return self

    def _set_defaultattributen(self):
        self.Punt = {}
        self.Meta = {}
        self.Data = np.array([])
        self.Tijd = []
        self.Tijdmin = []

    def set_itdate(self, itdate=None):
        if itdate is None:
            if 'itdate' in self.Meta is not True:
                #d = raw_input('Dag itdate: ')
                #m = raw_input('Maand itdate: ')
                d = input('Dag itdate: ')
                m = input('Maand itdate: ')

                y = ''
                while len(y) != 4:
                    #y = raw_input('Jaar itdate: ')
                    y = input('Jaar itdate: ')

                    if len(y) != 4:
                        print('geef met 4 digits weer')
                itdate = datetime.datetime.strptime(d+m+y, '%d%m%Y')
                self.Meta.update({'itdate': itdate})
            else:
                pass
        else:
            self.Meta.update({'itdate': itdate.strftime('%d %b %Y')})

    def set_data(self, a, b):
        self.Data = self.Data*a+b

    def return_datetime2timemin(self, T):
        itdate = self.Meta['itdate']
        tdelta = T-datetime.datetime.strptime(itdate, '%d %b %Y')
        tmin = tdelta.total_seconds()/60.

        return tmin

#class _FuncTs_special(object):
#    def __sub__(self, timeseriesobj):
#        assert self.__class__.__name__ == timeseriesobj.__class__.__name__
#
#        diffpunt = self.compare_puntobject(timeseriesobj.Punt)
#        #assert len(diffpunt) == 0
#
#        diffPunt = self.Punt.copy()
#        puntnummers = self.return_puntlist()[0]
#        for d in diffpunt:
#            puntnummers.remove(d)
#            diffPunt.pop(d)
#        #print(diffPunt)
#        try:
#            diffdata = np.zeros([self.Data.shape[0], len(puntnummers)])
#            for p in puntnummers:
#                colnr1 = self.Punt[p]['ColNR']
#                data1 = self.Data[:, colnr1]
#                colnr2 = timeseriesobj.Punt[p]['ColNR']
#                data2 = timeseriesobj.Data[:, colnr2]
#                diffdata[:, colnr1] = data1-data2
#        except AttributeError:
#
#            diffdata = list()#np.zeros([self.Data[0].shape, len(puntnummers)]).T
#            #print(len(diffdata))
#            for p in puntnummers:
#
#                colnr1 = self.Punt[p]['ColNR']
#                data1 = self.Data[colnr1]
#                colnr2 = timeseriesobj.Punt[p]['ColNR']
#                data2 = timeseriesobj.Data[colnr2]
#                print(len(data1))
#                print(len(data2))
#
#                diffdata.append(data1-data2)
#
#        diffMeta = self.Meta.copy()
#        try:
#            print('grrrr')
#            diffMeta['filename'] = self.Meta['filename']+'-'+timeseriesobj.Meta['filename']
#        except:
#            pass
#
#        diffdict = {'Data':diffdata, \
#                    'Tijd':self.Tijd, \
#                    'Meta':diffMeta, \
#                    'Punt':diffPunt, \
#                    'Tijdmin':self.Tijdmin}
#        diffobj = self.__class__(diffdict, None)
#        return diffobj

class _FuncTsIrregular(_FuncTs):
    def __init__(self):
        _FuncTs.__init__()

    def _set_tijdmin(self):
        self.set_itdate()
        itdatetime = datetime.datetime.strptime(self.Meta['itdate'], '%d %b %Y')
        for a, Tijd in enumerate(self.Tijd):
            # Tijddatetime = self.Tijd[colnr]
            T = np.zeros((len(Tijd)))
            #for b in range(len(Tijd)):
            for b in enumerate(Tijd):
                #T[b] = (Tijd[b] - itdatetime).total_seconds() / 60
                T[b[0]] = (b[1] - itdatetime).total_seconds() / 60
            self.Tijdmin.append(T)

    def _return_tijdminarray(self, colnr, itdate=None):
        """
        return array met (opgevulde) tijdreeks van tstart tot tstop.
        Input:
            - colnr = > kolomnr in self.Tijdmin [int]
        Output:
            - reeks met tijdstippen in minuten vanaf tstart tot tstop [numpy array, tstart....tstop]
        """
        if self.Tijdmin == []:
            if 'itdate' in self.Meta is not True or itdate is not None:
                self.set_itdate(itdate)
            self._set_tijdmin()

        Tijdmin = self.Tijdmin[colnr]
        return Tijdmin

    def _return_datetimearray(self, colnr, itdate=None):
        """ Return array met (opgevulde) tijdreeks van tstart tot tstop.

        Input:
            - colnr = > kolomnr in self.Tijdmin [int]
            - itdate => datetime-object.
        Output:
            reeks met tijdstippen in datetime-objecten vanaf tstart tot tstop
            [numpy array, datetime-object.....datetime-object]
        """

        if self.Tijd == []:
            if 'itdate' in self.Meta is not True or itdate is not  None:
                self.set_itdate(itdate)

            itdatetime = datetime.datetime.strptime(self.Meta['itdate'], '%d %b %Y')
            for a, Tijdmin in enumerate(self.Tijdmin):
                T = np.array([])
                for b in range(len(Tijdmin)):
                    # print(datetime.timedelta(0, int(Tmin[a]*60), 0))
                    T = np.append(T, itdatetime + datetime.timedelta(0, int(Tijdmin[b] * 60), 0))
                self.Tijd.append(T)

        Tijd = self.Tijd[colnr]
        return Tijd

class _FuncTsRegular(_FuncTs):
    """Class voor generieke Functies voor tijdseries Waqua"""
    def __init__(self):
        _FuncTs.__init__()

    def return_indextimestamps(self, T, colnr):
        """zoek index nummer in self.Data voor tijdstip in minuten tov itdate.

        Input:
            - T= tijdstip [integer in minuten of datetime.datetime -object]
            - colnr = kolom nr in self.Tijdmin[integer]
        Output:
            index nummer corresponderend met T  in self.Tijdmin[:, colnr] [integer]
        """

        if isinstance(T, datetime.datetime):
            T = self._return_datetime2timemin(T)

        Tmin = self._return_tijdminarray(colnr)
        ind = np.where(Tmin == T)
        return ind


    def _set_tijdmin(self):
        self.set_itdate()
        itdatestr = self.Meta['itdate']
        itdate = datetime.datetime.strptime(itdatestr, '%d %b %Y')
        for a in range(len(self.Punt)):
            if len(self.Tijd) == 1:
                T = self.Tijd[0]
            else:
                T = self.Tijd[a]
            tint = (T[1]-T[0]).total_seconds()/60.
            tstart = (T[0]-itdate).total_seconds()/60.
            teind = (T[-1] - itdate).total_seconds() / 60.
            self.Tijdmin.append([tstart, teind, tint])

    def _return_tijdminarray(self, cnr=None):
        """
        return array met (opgevulde) tijdreeks van tstart tot tstop.
        Input:
            - colnr = > kolomnr in self.Tijdmin [int]
        Output:
            - reeks met tijdstippen in minuten vanaf tstart tot tstop [numpy array, tstart...tstop]
        """
        if cnr is None:
            cnr = 0

        if self.Tijdmin == []:
            self._set_tijdmin()
        tijdmin = np.arange(self.Tijdmin[cnr][0], self.Tijdmin[cnr][1]\
                +self.Tijdmin[cnr][2], self.Tijdmin[cnr][2])
        return tijdmin

    def _return_datetimearray(self, colnr, itdate=None):
        """

        return array met (opgevulde) tijdreeks van tstart tot tstop.

        Input:

            - colnr = > kolomnr in self.Tijdmin [int]
            - itdate => datetime-object.
        Output:

            reeks met tijdstippen in datetime-objecten vanaf tstart tot tstop

            [numpy array, datetime-object.....datetime-object]
        """
        if itdate != None:
            self.set_itdate(itdate)

        tstart = self.Tijdmin[colnr][0]
        tend = self.Tijdmin[colnr][1]+self.Tijdmin[colnr][2]
        tint = self.Tijdmin[colnr][2]
        Tmin = np.arange(tstart, tend, tint)
        Tijd = np.zeros((len(Tmin)), dtype=datetime.datetime)

        itdate = datetime.datetime.strptime(self.Meta['itdate'], '%d %b %Y')
        #for a in range(len(Tmin)):
        #    Tijd[a] = itdate+datetime.timedelta(0, Tmin[a]*60, 0)
        for a in enumerate(Tmin):
            Tijd[a[0]] = itdate+datetime.timedelta(0, a[1]*60, 0)

        return Tijd

    @decorate_write
    def write_timeseriesregular(self, outputfile, outputdir, tstart, tstop, \
        list_naampuntnr, repeat=1, constit=None):
        """ Schrijf file met regelmatige tijdreeks.
        Input:
            - outputfile => naam uitvoerbestand [string]
            - outputdir => naam uitvoerpad [string]
            - tstart => starttijdstip in minuten voor weg te schrijven tijdreeks  [integer]
            - tstop => eindtijdstip in minuten voor weg te schrijven tijdreeks [integer]
            - list_naampuntnr => lijst van punt-objecten[iterable van waquagrid_toolkit.Punt-object]
            - repeat= herhaal tijdreeks [integer].
            - constit= nummer constituent, indien constituent [None of int]
        """
        g = open(os.path.join(outputdir, outputfile), 'w')
        x = 0

        if isinstance(list_naampuntnr, str):
            list_naampuntnr = [list_naampuntnr]
        for nm in list_naampuntnr:
            if isinstance(nm, Punt):
                naam = nm[0]
                puntnr = nm[1]
                puntsel = self.return_naamselect(naam)
                #print(len(puntsel))
                assert len(puntsel) < 2, 'selecteer naam dat maar bij 1 punt hoort'
            else:
                naam = nm
                puntsel = self.return_naamselect(nm)
                assert len(puntsel) < 2, 'selecteer naam dat maar bij 1 punt hoort, '+str(puntsel)
                puntnr = [*puntsel.keys()][0]
                
            print(puntnr)
            ind_start = self.return_indextimestamps(tstart, 0)[0]
            ind_stop = self.return_indextimestamps(tstop, 0)[0]
            colnr = self.Punt[puntnr]['ColNR']
            #print(colnr)
            #print(ind_start[0])
            #print(ind_stop[0])
            if isinstance(self.Data, list):
                val = self.Data[colnr][ind_start[0]:ind_stop[0]+1]
            else:
                val = self.Data[ind_start[0]:ind_stop[0]+1, colnr]
            if len(self.Tijdmin) == 1:
                tint = self.Tijdmin[0][2]
            else:
                tint = self.Tijdmin[colnr][2]
            tstop_frameline = tstart+repeat*(tint+tstop-tstart)-tint
            if constit is None:
                puntline = '   S: P   '+str(puntnr)+' ,   TID= '+str(val[0])+\
                '   ,   SERIES = \'regular\' \n'
            else:
                assert type(constit) == int
                puntline = '   TS: CO' +str(constit)+', P   '+str(puntnr)+\
                ' ,   CINIT= '+str(val[0])+ '   ,   SERIES = \'regular\' \n'
            frameline = '      FRAME= ( ' +str(tstart)+'    ,  '+str(tint)+\
            '   ,   '+str(tstop_frameline)+ '     )\n'
            valuesline = '     VALUES= \n'
            g.write(puntline)
            g.write(frameline)
            g.write(valuesline)
            i = 0
            for a in range(repeat):
                for v in val:
                    g.write(str(v)+'  ')
                    if i == 3:
                        g.write('\n')
                        i = 0
                    else:
                        i = i+1
            g.write('\n')
            x = x+1
        g.close()

class _PlotTs(Punt, _FuncTs):
    """Class voor generieke plotfuncties tijdseries Waqua"""
    def __init__(self):
        _FuncTs.__init__()

    def __volgordeplotting(self, selectie, **kwargs):
        """    a) Bepaal volgorde waarin geselecteerde lijnen geplot worden.
               b) Verwijder parameter volgorde uit kwargs
        Input:
            - selectie => [iterable].
            - kwargs => afkomstig uit functies plot_ts...
        Output:
            volgorde => list van integers, met volgorde waarin lijnen geplot moeten worden
            kwargs => kwargs, eventueel zonder keyword volgorde
        """

        if 'volgorde' in kwargs:
            volgorde = kwargs.pop('volgorde')
            #print(volgorde)
        else:
            volgorde = range(len(selectie))
        return volgorde, kwargs

    def _kwargs_handling(self, selectie, **kwargs):
        volgorde, kwargs = self.__volgordeplotting(selectie, **kwargs)

        if 'itdate' in kwargs:
            itdate = kwargs.pop('itdate')
            assert isinstance(itdate,(bool, datetime.datetime)), 'incorrecte waarde voor itdate'
            if itdate is True:
                assert 'itdate' in self.Meta, 'itdate ontbreekt nog in Meta'
        else:
            itdate = 0

        return volgorde, itdate, kwargs

    def _plot_tsselectie(self, selectie, volgorde, itdate, *arg, **kwargs):
        """Plot geselecteerde lijnen. Wordt aangeroepen in plot_ts functies.

        Input:
            a) selectie: dictionary afkomstig uit Punt:
                key:{'m':int, 'n':int, 'name':str, ('x':float, 'y':float)}
            b) volgorde: volgorde waarin lijnen geplot worden. [iterable
            c)itdate: opties:
                1) False => tijd in minuten
                2) True => datetime.datetime-object uit self.Meta['itdate']
                3) datetime.datetime-object
            d) args en kwargs => zie matplotlib.pyplot.plot

        Output:
            lijnen grafiek
        """

        assert isinstance(selectie, dict)

        leg = []
        selkeys = [*selectie.keys()]
        #print(volgorde)
        #print(selectie)
        #print(selkeys)
        for v in volgorde:
            s = selectie[selkeys[v]]
            colnr = s['ColNR']

            if itdate is True:
                self
                Tijd = self.Tijd[0]
            else:
                if len(self.Tijd) == 1:
                    colnrT = 0
                else:
                    colnrT = colnr
                if not itdate:
                    if len(self.Tijdmin[colnrT]) == 3 and \
                    self.Tijdmin[colnrT][2] < self.Tijdmin[colnrT][1]:
                        t1 = self.Tijdmin[colnrT][0]
                        t2 = self.Tijdmin[colnrT][1]+self.Tijdmin[colnrT][2]
                        deltat = self.Tijdmin[colnrT][2]
                        Tijd = np.arange(t1, t2, deltat)

                    else:
                        Tijd = self.Tijdmin[colnrT]
                elif isinstance(itdate, datetime.datetime):
                    Tijd = self._return_datetimearray(colnrT, itdate)
            if isinstance(self.Data, list):
                data = self.Data[colnr]
            elif isinstance(self.Data, np.ndarray):
                data = self.Data[:, colnr]
            else:
                raise TypeError('self.Data heeft incorrect data type')

            pyl.plot(Tijd, data, *arg, **kwargs)
            leg.append(s['name'])
        pyl.legend(leg)

    @decorate_plot
    def plot_tsnaam(self, naamselectie, strikt=False, *arg, **kwargs):
        """plot tijdreeksen op basis van (Gedeelte) van de punt naam.
        Input:
            - naamselectie => string (case INsensitive)
            - *arg: input parameters zie matplotlib.pyplot.plot
            - **kwargs: A) input parameters zie matplotlib.pyplot.plot \n
                    B) andere optionele keywords kwargs <volgorde > , of <itdate > \n
                    - kw['volgorde']= volgorde waarin lijnen geplot worden [iterable]
                    - kw['itdate'] = > itdate (datetime.datetime-object )
                            om data ten opzichte van te plotten
        Output:
            Lijnen grafiek.

        Bijvoorbeeld: Er zijn drie locaties met Vlaardingen in de naam.

        Deze wil je plotten in omgekeerde volgorde.
        self.plot_tsnaam('Vlaardingen', volgorde = [2, 1,0])

            1) alle locaties waar vlaardingen in de naam voorkomt worden geplot
            2) Volgorde lijnen wordt omgedraaid.
        """

        if isinstance(naamselectie, str):
            sel = self.return_naamselect(naamselectie, strikt)
        else:
            sel = {}
            for name in naamselectie:

                seltemp = self.return_naamselect(name, strikt)
                for p, v in seltemp.items():
                    sel.update({p:v})

        volgorde, itdate, kwargs = self._kwargs_handling(sel, **kwargs)
        print(volgorde)
        self._plot_tsselectie(sel, volgorde, itdate, *arg, **kwargs)

    @decorate_plot
    def plot_tsxybox(self, xybox, *arg, **kwargs):
        """Plot tijdreeks op basis van een boundingbox

        Input:

            - xybox => bounding box [xmin, xmax, ymin, ymax]

            - *arg en **kwargs: zie self.plot_tsnaam
        Output:
            Lijnen grafiek

        Bijvoorbeeld: sel.plot_tsxybox([-1000, 1000, 2000, 4000], 'k', axes = ax)
            plot punten die vallen binnen x = -1000 tot x = 1000 en y =2000 en y = 4000\n
            kleur lijnen is zwart, as heeft handle ax.
        """
        sel = self._return_xyboxselect(xybox)

        volgorde, itdate, kwargs = self._kwargs_handling(sel, **kwargs)
        self._plot_tsselectie(sel, volgorde, itdate, *arg, **kwargs)

    @decorate_plot
    def plot_tsnummers(self, nummers, *arg, **kwargs):
        """Plot tijdreeks op basis van nummers zoals key in class variabele Punt staat.

        Input:

            - nummers => puntnummers[iterable]
             Met self.Punt.keys() zie je welke nummers je kan opgeven

            - *arg en **kwargs: zie self. plot_tsnaam
        Bijvoorbeeld: self.plot_tsnummers([10, 3,2], volgorde = [2, 1,0], 'k', axes = ax)
            plot punten met puntnummer 10, 3 en 2\n
            plot lijnen in omgekeerde volgorde.
        """
        try:
            sel = self.return_nummerselect(nummers)
        except TypeError:
            sel = self.return_nummerselect([nummers])

        volgorde, itdate, kwargs = self._kwargs_handling(sel, **kwargs)
        print(itdate)
        self._plot_tsselectie(sel, volgorde, itdate, *arg, **kwargs)

    @decorate_plot
    def plot_tscolnr(self, nummers, *arg, **kwargs):
        """Plot tijdreeks op basis van nummers zoals key in class variabele Punt staat.

        Input:

            - nummers => columnnummers[iterable]
             Met self.Punt.keys() zie je welke nummers je kan opgeven

            - *arg en **kwargs: zie self. plot_tsnaam
        Bijvoorbeeld: self.plot_tsnummers([10, 3,2], volgorde = [2, 1,0], 'k', axes = ax)
            plot punten met puntnummer 10, 3 en 2\n
            plot lijnen in omgekeerde volgorde.
        """
        if hasattr(nummers, '__iter__') is not True:
            nummers = [nummers]
        numsel = [p for p in self.Punt if self.Punt[p]['ColNR'] in nummers]
        #numsel = [p for p in self.Punt if self.Punt[p]['ColNR'] in nummers]
        sel = {}
        for n in numsel:
            sel.update({n:self.Punt[n]})
            #print(sel)

        volgorde, itdate, kwargs = self._kwargs_handling(sel, **kwargs)
        self._plot_tsselectie(sel, volgorde, itdate, *arg, **kwargs)

    #@decorate_plot
    def plot_colnrdict(self, xveld=[], yveld=[], ax=[], *arg, **kwarg):
        """Plot in kaart columnnummers waarin data staan.
        Handig in combinatie met method plot_tscolnr """

        def return_colnrdict(self):
            colnrdict = {}
            for k, v in self.Punt.items():
                v.update({'puntnr':k})

                #print(v)
                colnrdict.update({v.pop('ColNR'):v})
            return colnrdict

        dictcolnr = return_colnrdict(self)
        xlist = []
        ylist = []
        for a in dictcolnr.keys():
            naam = str(a)
            if 'x' in dictcolnr[a]:
                x = float(dictcolnr[a]['x'])
                y = float(dictcolnr[a]['y'])
            elif xveld == []:
                x = float(dictcolnr[a]['n'])
                y = float(dictcolnr[a]['m'])
            else:
                x = xveld[dictcolnr[a]['m'], dictcolnr[a]['n']]
                y = yveld[dictcolnr[a]['m'], dictcolnr[a]['n']]
            xlist.append(x)
            ylist.append(y)
            pyl.text(x, y, naam, *arg, **kwarg)
            pyl.plot(x, y, 'ko')
        pyl.xlim(min(xlist), max(xlist))
        pyl.ylim(min(ylist), max(ylist))

#class Getdatacsv(_PlotTs, _FuncTsRegular, _FuncTs_special):
class Getdatacsv(_PlotTs, _FuncTsRegular):
    """ Class voor csv files, gemaakt met getdata.pl"""

    def __init__(self, inp1, tpad):
        """Input:
            - inp1 = > a)filenaam [string] b) getdatacsv-instance
            - tpad => filepad [string]
        Attributen:
            - self.Tijdmin: list met per punt bestaande uit list tstop, teind, tint  [int, in, int]
            - self.Data: list met per punt array [numpy array]

            - self.Punt: punt object van data uit Tijdmin en Data
            - self.Meta: metadata uit header csv-file [dictionary]

        """

        if isinstance(inp1, str):
            tfile = inp1
            self._set_defaultattributen()
            if 'RRSBAH' in tfile:
                tr = inlw().getdatacsv_barrier(tfile, tpad)
            else:
                tr = inlw().getdatacsv(tfile, tpad)

            if tr[1][1]-tr[1][0] != tr[1][2]-tr[1][1]:
                #history start later dan T = 0 berekening
                self.Tijd = [tr[1][1:], ]
                self.Data = tr[2][1:]
                self.Tijdmin = [[tr[3][1], tr[3][-1], tr[3][2]-tr[3][1]], ]
            else:
                self.Tijd = [tr[1], ]
                self.Data = tr[2]
                self.Tijdmin = [[tr[3][0], tr[3][-1], tr[3][1]-tr[3][0]], ]
            x = 0
            self.Punt = {}
            for t in tr[0]:
                nr = x
                name = t
                dictio = tr[0][t]
                if 'm' in dictio:
                    dictio.update({'name':name})
                    self.Punt.update({nr:dictio})
                    x = x+1
                else:
                    self.Meta.update(dictio)
        else:
            assert isinstance(inp1, dict)
            self._copy_wstkattributen(inp1)

    def __sub__(self, timeseriesobj):
        assert self.__class__.__name__ == timeseriesobj.__class__.__name__

        diffpunt = self.compare_puntobject(timeseriesobj.Punt)
        #assert len(diffpunt) == 0

        diffPunt = self.Punt.copy()
        puntnummers = self.return_puntlist()[0]
        for d in diffpunt:
            puntnummers.remove(d)
            diffPunt.pop(d)
        #print(diffPunt)
        try:
            diffdata = np.zeros([self.Data.shape[0], len(puntnummers)])
            for p in puntnummers:
                colnr1 = self.Punt[p]['ColNR']
                data1 = self.Data[:, colnr1]
                colnr2 = timeseriesobj.Punt[p]['ColNR']
                data2 = timeseriesobj.Data[:, colnr2]
                diffdata[:, colnr1] = data1-data2
        except AttributeError:

            diffdata = list()#np.zeros([self.Data[0].shape, len(puntnummers)]).T
            #print(len(diffdata))
            for p in puntnummers:

                colnr1 = self.Punt[p]['ColNR']
                data1 = self.Data[colnr1]
                colnr2 = timeseriesobj.Punt[p]['ColNR']
                data2 = timeseriesobj.Data[colnr2]
                print(len(data1))
                print(len(data2))

                diffdata.append(data1-data2)

        diffMeta = self.Meta.copy()
        try:
            print('grrrr')
            diffMeta['filename'] = self.Meta['filename']+'-'+timeseriesobj.Meta['filename']
        except:
            pass

        diffdict = {'Data':diffdata, \
                    'Tijd':self.Tijd, \
                    'Meta':diffMeta, \
                    'Punt':diffPunt, \
                    'Tijdmin':self.Tijdmin}
        diffobj = self.__class__(diffdict, None)
        return diffobj

    @decorate_plot
    def plot_tsalles(self, *arg, **kwargs):
        """ Plot alle lijnen,

        Input:
            *arg en *kwargs: zie matplotlib.pyplot.plot
        Output:
            lijnen grafiek
        """
        for k, v in self.Punt.items():
            colnr = v['ColNR']
            pyl.plot(self.Tijd[0], self.Data[:, colnr], *arg, **kwargs)

    """
    @decorate_write
    def write_timeseriesregular(self, outputfile, outputdir, tstart, tstop, list_naampuntnr, repeat = 1, constit = None):
        \""" Schrijf file met regelmatige tijdreeks.
        Input:
            - outputfile => naam uitvoerbestand [string]
            - outputdir => naam uitvoerpad [string]
            - tstart => starttijdstip in minuten voor weg te schrijven tijdreeks  [integer]
            - tstop => eindtijdstip in minuten voor weg te schrijven tijdreeks [integer]
            - list_naampuntnr => lijst van punt-objecten[iterable van waquagrid_toolkit.Punt-object]
            - repeat= herhaal tijdreeks [integer].
            - constit= nummer constituent, indien constituent [None of int]
        \"""
        g = open(os.path.join(outputdir, outputfile), 'w')
        x = 0

        for nm in list_naampuntnr:
            if isinstance(nm, Punt):
                naam = nm[0]
                puntnr = nm[1]
                puntsel = self.return_naamselect(naam)
                print(len(puntsel))
                assert len(puntsel) <  2, 'selecteer naam dat maar bij 1 punt hoort'
            else:
                naam =nm
                puntsel = self.return_naamselect(nm)
                assert len(puntsel) < 2, 'selecteer naam dat maar bij 1 punt hoort'
                puntnr = puntsel.keys()[0]

            ind_start = self.return_indextimestamps(tstart, 0)[0]
            ind_stop = self.return_indextimestamps(tstop, 0)[0]
            colnr = self.Punt[puntnr]['ColNR']
            val = self.Data[ind_start[0]:ind_stop[0]+1, colnr]
            tint = self.Tijdmin[colnr][2]
            tstop_frameline = tstart+repeat*(tint+tstop-tstart)-tint
            if constit is None:
                puntline = '   S: P   '+str(puntnr)+' ,   TID= '+str(val[0])+ '   ,   SERIES = \'regular\' \n'
            else:
                assert type(constit) == int
                puntline = '   TS: CO' +str(constit)+', P   '+str(p)+' ,   CINIT= '+str(val[0])+ '   ,   SERIES = \'regular\' \n'
            frameline = '      FRAME= ( ' +str(tstart)+'    ,  '+str(tint)+'   ,   '+str(tstop_frameline)+ '     )\n'
            valuesline = '     VALUES= \n'
            g.write(puntline)
            g.write(frameline)
            g.write(valuesline)
            i = 0
            for a in range(repeat):
                for v in val:
                    g.write(str(v)+'  ' )
                    if i == 3:
                        g.write('\n')
                        i = 0
                    else:
                        i = i+1
            g.write('\n')
            x = x+1
        g.close()
        """
class Timeseries_regular(_PlotTs, _FuncTsRegular):
    """Class voor generieke plotfuncties regelmatige tijdseries Waqua
    regelmatige tijdseries zien eruit als:
        S: P         9000 ,   TID=    1.413454     ,   SERIES = 'regular'\n
        FRAME= (    8850.000     ,   1.000000     ,   18930.00      )\n
        VALUES= \n
        0.1413454E+01  0.1418507E+01  0.1415292E+01  0.1419621E+01\n
        0.1416318E+01  0.1424202E+01  0.1425143E+01  0.1429200E+01\n
        etcetera

    Attributen:
        - self.Tijd
        - self.Tijdmin
        - self.Data
        - self.Punt
        - self.Meta
    """
    def __init__(self, inp1, tpad, puntfile, puntpad):
        """Input:
            - inp1 = > a)filenaam [string] b) Timeseries_regular-instance
            - tpad => filepad [string]
            - puntfile => filenaam puntfile [string]
            - puntpad =>filepad puntfile [string]
        Attributen:
            - self.Tijdmin: list met per punt bestaande uit list tstop, teind, tint  [int, in, int]
            - self.Data: list met per punt array [numpy array]
            - self.Punt: punt object van data uit Tijdmin en Data
        """
        if isinstance(inp1, str):
            self._set_defaultattributen()
            tr = inlw().timeseries_regular(inp1, tpad)
            for time in tr[1]:
                tstart = time[0]
                tend = time[-1]
                tint = time[1]-time[0]
                #Besparen op geheugenruimte !!!!
                self.Tijdmin.append([tstart, tend, tint])
            self.Data = tr[2]

            punt = Punt(puntfile, puntpad)
            self.Punt = punt.return_nummerselect(tr[0])
            for ColNR in range(len(tr[0])):
                puntnr = tr[0][ColNR]
                #print(puntnr)
                dictio = self.Punt[puntnr]
                dictio.update({'ColNR':ColNR})
                self.Punt.update({puntnr:dictio})
        else:
            self._copy_wstkattributen(inp1)

    @decorate_plot
    def plot_tsalles(self, itdate, *arg, **kwargs):
        """ Plot alle punten,

        Input:
            *arg en *kwargs: zie matplotlib.pyplot.plot
        Output:
            lijnen grafiek
        """

        for p in self.Punt:
            colnr = self.Punt[p]['ColNR']
            Data = self.Data[colnr]
            if itdate is False:
                tb, ts, tint = self.Tijdmin[colnr]
                Tijd = np.arange(tb, ts+tint, tint)
            else:
                Tijd = self._return_datetimearray(colnr, itdate)
            #return Tijd, Data
            pyl.plot(Tijd, Data)
class Timeseries_irregular(_PlotTs, _FuncTsIrregular):
    """Class voor generieke plotfuncties regelmatige tijdseries Waqua
    regelmatige tijdseries zien eruit als:
    S:P221 TID = ,  -831.0, SERies = 'irregular'\n
    TIME_and_VALUES=       11   0:00        -831.0\n
    TIME_and_VALUES=       12   0:00        -763.0\n
    TIME_and_VALUES=       13   0:00        -710.0\n
    TIME_and_VALUES=       14   0:00        -596.0\n
    TIME_and_VALUES=       15   0:00        -564.0\n
    TIME_and_VALUES=       16   0:00        -540.0\n
    Attributen:
        - self.Tijdmin: list met per punt bestaande uit list tstop, teind, tint  [int, in, int]
        - self.Data: list met per punt array [numpy array]
        - self.Punt: punt object van data uit Tijdmin en Data
    """

    def __init__(self, inp1, tpad, puntfile, puntpad):
        """Input:
            - inp1 = > a)filenaam [string] b) Timeseries_irregular-instance
            - tpad => filepad [string]
            - puntfile => filenaam puntfile [string]
            - puntpad =>filepad puntfile [string]
        """
        self._set_defaultattributen()
        if isinstance(inp1, str):
            #self._set_defaultattributen()
            tfile = inp1
            print(tfile)
            print(tpad)
            tr = inlw().timeseries_irregular(tfile, tpad)
            punt = Punt(puntfile, puntpad)
            #Class Variabele Punt
            #Toevoegen kolomnummer Data aan puntnummers
            self.Punt = punt.return_nummerselect(tr[0])
            for ColNR in range(len(tr[0])):
                puntnr = tr[0][ColNR]
                #print(puntnr)
                dictio = self.Punt[puntnr]
                dictio.update({'ColNR':ColNR})
                self.Punt.update({puntnr:dictio})
            #print(self.Punt)
            #class-variabele Tijd
            self.Tijdmin = tr[1]

            #Class Variabele Data
            self.Data = tr[2]
            self.Tijd = []
        else:
            self._copy_wstkattributen(inp1)

class Timeseries_irregular_wind(_FuncTsIrregular):
    """Class voor generieke plotfuncties regelmatige tijdseries Waqua
    regelmatige tijdseries zien eruit als:
    S:P221 TID = ,  -831.0, SERies = 'irregular'\n
    TIME_and_WINDVALUES=       11   0:00        21.0 100 \n
    TIME_and_WINDVALUES=       12   0:00        10.0  90 \n
    TIME_and_WINDVALUES=       13   0:00        10.0  85 \n
    TIME_and_WINDVALUES=       14   0:00        6.0   47 \n
    TIME_and_WINDVALUES=       15   0:00        4.0  150 \n
    TIME_and_WINDVALUES=       16   0:00        4.0  245 \n
    Attributen:
        - self.Tijdmin: list met per punt bestaande uit list tstop, teind, tint  [int, in, int]
        - self.Data: list met per punt array [numpy array]
    """

    def __init__(self, inp1, wpad):
        """Input:
            - inp1 = > a)filenaam [string] b) Timeseries_irregular-instance
            - tpad => filepad [string] of iets anders
        """
        if isinstance(inp1, str):
            self._set_defaultattributen()
            wfile = inp1
            tr = inlw().timeseries_irregular_wind(wfile, wpad)
            #class-variabele Tijd
            self.Tijdmin = [tr[0], tr[0]]
            #Class Variabele Data
            self.Data = tr[1]
            #self = wstk.set_defaultmeta(self)#self.Meta = {}
            #self.Tijd = []
        else:
            self._copy_wstkattributen(inp1)

#class Adobs(Punt, _PlotTs, _FuncTsIrregular):
#class Adobs(_PlotTs, _FuncTsIrregular):
class Adobs(_FuncTsIrregular, Punt):
    def __init__(self, inp1, tpad):
        adobs_keys = ('zpos', 'zref', 'system', 'zone', 'offset', 'dummy', 'unit')
        if isinstance(inp1, str):
            self._set_defaultattributen()
            tfile = inp1
            tr = inlw().adobs(tfile, tpad)
            #punt = Punt(puntfile, puntpad)
            self.Tijd = [tr[1]]
            self.Data = [tr[2]]
            self.Punt = {0:{'m':tr[0]['m'], 'n':tr[0]['n'], 'name':tr[0]['name'], \
            'ColNR':0}}
            for ad in adobs_keys:
                if ad in tr[0]:
                    self.Meta[ad] = tr[0][ad]

        else:
            self._copy_wstkattributen(inp1)

    def plot_tsalles(self, itdate=False, *arg, **kwargs):
        Data = self.Data[0]
        if itdate is not True:
            Tijd = self._return_tijdminarray(0)
        else:
            Tijd = self._return_datetimearray(0, itdate)
        pyl.plot(Tijd, Data, *arg, **kwargs)
