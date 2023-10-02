import gc
import os
import re

import numpy as np


class color_scheme(object):
    #startinlezencoloring = '\33[0;42m'
    #commentcoloring = '\33[0;32m'
    #endcoloring = '\33[0;0m'
    startinlezencoloring = u'\n \u001b[36m \u001b[40m'
    commentcoloring = u'\u001b[32;1m \u001b[1m'
    endcoloring = u'\u001b[0m'

def convDT(tijd, itdate):
    """" conversie tijd ten opzichte van itdate naar datenum object """
    import datetime #, numpy as np
    dt = datetime.datetime.strptime(itdate, r'%d %b %Y')
    tijd2 = []
    if isinstance(tijd, int):
        tijd2 = dt+datetime.timedelta(minutes=tijd)
    else:
        for t in tijd:
            tijd2.append(dt+datetime.timedelta(minutes=t))

        tijd2 = np.array(tijd2)
    return tijd2

def _asciiinlezen(pad, filename):
    """inlezen van een tekstfile in zijn geheel.

    Dit werkt voor files met de omvang van Waqua files heel snel."""
    padfile = os.path.join(pad, filename)
    assert (os.path.isdir(pad)), 'Incorrect pad: '+pad
    assert (os.path.isfile(padfile)), 'Incorrect file: '+padfile
    #print(color_scheme.startinlezencoloring+'inlezen'+ padfile;)
    with open(padfile, 'r') as fh:
        lines = list(fh)

    return lines

#regular expression voor commentline
def checkcommentline(line):
    #coloring = '\33[32m'
    coloring = color_scheme.commentcoloring
    #endcoloring = r'\33[0m'
    endcoloring = color_scheme.endcoloring
    COMMENTLINE = r'\s*?#|\s*$'
    textcomment = r'#(.+)$'

    #assert line.endswith('\n'), line+': Moet eindigen op \\n'
    test = re.match(COMMENTLINE, line) != None
    if test is True:
        renahashtag = re.search(textcomment, line)
        if renahashtag != None:
            textnahashtag = renahashtag.groups()[0].strip()
            #textnahashtag = re.search(textcomment, line).groups()[0].strip()
            if textnahashtag != '':
                print(coloring+'COMMENT: '+textnahashtag+color_scheme.endcoloring)
    return test


class veld(object):
    @staticmethod
    def rgf(filename, pad=os.getcwd()):
        """ Inlezen rgf-file"""
        #reETA = r'\s*ETA\s* = (.+)'
        print(color_scheme.startinlezencoloring+'start inlezen rgf'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        #Controleer inhoud file
        filecheck = False
        for l in lines[0:200]:
            filetest = re.search(r'^\s*(ETA\s*.+)$', l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als rgf-file. Verkeerde filetype??'

        print(u'\tstart fase1: bepaal afmetingen grid')
        x = 0
        m_nr = -1
        n_nr = -1
        try:
            while m_nr == -1:

                if(lines[x].strip()[0] == '*')|(lines[x].strip()[0] == '#'):
                    x = x+1
                    continue
                elif lines[x].strip()[0:4].upper() == 'COOR':
                    x = x+1
                    continue
                elif len(lines[x].strip()[0]) > 1:
                    x = x+1
                    print(u'\t'+lines[x].strip()[0])
                elif len(lines[x].split()) > 1:
                    try:
                        m_nr = int(lines[x].split()[0])
                        n_nr = int(lines[x].split()[1])
                    except ValueError:
                        x = x+1
                        continue
                    x = x+1
        except:
            raise Exception( 'regel'+str(x+1)+': '+lines[x])
        print('afmetingen grid = '+str(m_nr+1)+ ' bij '+ str(n_nr+1))
        print(u'\tfase1: gereed')

        #grid = np.array([])
        grid = np.zeros([2, m_nr+1, n_nr+1], dtype=np.float)
        print(u'\tstart fase2: inlezen xdep')
        k = -1
        i = 0
        j = 0
        x = x+1
        for l in lines[x:]:
            test = checkcommentline(l)
            if test is True:
                continue

            temp1 = re.match(r'\s*ETA\s*=(.+)', l, re.I)
            if temp1 is None:
                temp2 = l.split()
                for a in temp2:
                    if a[0] != '#' and a[0] != '*':
                        #grid[k, i, j] = np.float(a)
                        grid[k, i, j] = a
                        if i < m_nr-1:
                            i = i+1
                        else:
                            i = 0
                            j = j+1
                    else:
                        break # comment na #
            else:
                temp2 = temp1.groups()[0].split()
                if temp2[0] == '***':
                    #if k == 0:
                    #k = k+1;
                    #else:
                    #k = 0
                    #j = j+1;
                    print(u'\tjolo')
                elif int(temp2[0]) == 1:
                    if k == 0:
                        print(u'\tfase2: gereed')
                        print(u'\tstart fase3: inlezen ydep')
                        k = k+1
                    else:
                        k = 0
                    i = 0
                    j = 0
                #else:
                #    print('gaat dit wel goed?')

                for a in temp2[1:]:
                    if a[0] != '#':
                        #print(k, i, j)
                        #grid[k, i, j] = np.float(a)
                        grid[k, i, j] = a
                        if i < m_nr-1:
                            i = i+1
                        else:
                            #print('inlezen volgende veld.')
                            i = 0
                            j = j+1
                    else:
                        break
        print(u'\teinde fase3')
        xdep = grid[0]
        ydep = grid[1]
        xdep = np.ma.masked_values(xdep, 0.,copy=True)
        ydep = np.ma.masked_values(ydep, 0.,copy=True)
        print(xdep)
        np.place(xdep, xdep == 0., np.nan)
        np.place(ydep, ydep == 0., np.nan)
        print(xdep)
        print('inlrgf gereed')
        return xdep, ydep

    @staticmethod
    def getdatamat(filename, pad=os.getcwd()):
        """ inlezen waqua matfiles gemaakt met getdata """
        import scipy.io as matimp

        print(color_scheme.startinlezencoloring+\
        'inlezen getdata-mat bestand'+\
        color_scheme.endcoloring)
        padfile = os.path.join(pad, filename)
        #assert os.path.splitext(file)[1] == '.mat', 'Geen matfile'
        try:
            veld = matimp.loadmat(padfile)
        except ValueError:
            print('Geen matfile opgegeven?')

        assert len(veld.keys()) == 1
        #x = veld.keys()[0]#veld = veld[(x)] #let op gebruik van [] rond de (x)
        print(veld)
        veld = [*veld.values()][0]
        #print(veld)
        veld = veld.T
        #masker aanbrengen op maximale waarde.
        masker = veld == veld.max()
        veld = np.ma.masked_array(veld, mask=masker)
        np.place(veld, veld == veld.max(), np.nan)
        return veld

    @staticmethod
    def box(filename, pad=os.getcwd()):
        """inlezen box-files"""
        reBOX = r'\s*BOX\D*(\d+)\D*(\d+)\D*(\d+)\D*(\d+)\D*'
        #reLayer = r'LAYER\s* = \s*(\d+)'

        print(color_scheme.startinlezencoloring+'inlezen box-file'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        #Check bestand
        filecheck = False
        for l in lines[0:200]:
            filetest = re.search(reBOX, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als box-file. Verkeerde filetype??'

        print(u'\tbepaal afmetingen boxfile')
        m_nr = 0
        n_nr = 0
        layer_nr = 1
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            #dim = re.search(r'\s*BOX\D*(\d+)\D*(\d+)\D*(\d+)\D*(\d+)\D*', l, re.I)
            dim = re.search(r'\s*BOX'+4*r'\D*(\d+)'+r'\D*', l, re.I)
            if dim != None:
                #print(dim.group(4))
                if int(dim.group(3)) > m_nr:
                    m_nr = int(dim.group(3))
                if int(dim.group(4)) > n_nr:
                    n_nr = int(dim.group(4))

                layer = re.search(r'LAYER\s*=\s*(\d+)', l, re.I)
                if layer != None:
                    layer_nr = int(layer.groups()[0])
                    #if layer_nr == 2:
                    #    layer_nr = 3
                    #    print(layer_nr)
                    #    raise exception
        if layer_nr == 0:
            layer_nr = 1
        print(u'\tafmetingen boxfile:')
        print(u'\tm = '+str(m_nr)+', n = '+str(n_nr)+', k = '+str(layer_nr))

        print(u'\tinlezen cellen')
        i = 0
        js = 0
        k = 0
        veld = np.zeros([m_nr, n_nr, layer_nr])

        lnr = 0
        for l in lines[:]:
            lnr = lnr+1

            test = checkcommentline(l)
            if test is True:

                continue
            if re.search(r'^\s*variable', l, re.I):
                #print(l)
                continue

            temp = l.upper().strip().split()
            #Comment regels
            #print(veld.shape)
            if temp != []:
                if (temp[0][0] == '#')|(temp[0][0] == '*'):
                    print(u'\t'+l)
                elif temp[0][0:3] != 'BOX':
                    #print(temp[0][0:3])
                    j = js
                    for a in temp[:]:
                        if a[0] != '#':
                            veld[i, j, k] = np.float(a)
                            j = j+1
                        else:

                            break
                    i = i+1
                else:
                    f = re.split(r'\,|\(|\)|\;', l)
                    js = int(f[2])-1
                    #print(f)
                    #print(js)
                    i = 0
                    i = int(f[1])-1
                    if layer_nr > 1:
                        k = int(f[-2].split()[-1])-1
        veld = veld.squeeze()

        print('inlbox gereed')
        return veld

class tijdreeks(object):
    @staticmethod
    def getdatacsv(filename, pad=os.getcwd()):
        """Created on May 05  2015
        inlezen van getdata-csv file met python.
        Omzetting naar waarden omzetten naar "Arrays data" en dictionary metadata in "stat"

        Output:
        stat: Dictionary
            key ='meta data
            : key overig = Locatienaam
                        dict onder locatienaam

        data = Array
                Kolomnr uit stat
                Rijnr: overeenkomend tijden

        tijd"""

        reREFERENCE = r'\s*\"Reference date\s* = '
        print(color_scheme.startinlezencoloring+\
        'inlezen getdata-csv bestand'+\
        color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)
        #print('ggrrrrr')
        #Check bestand
        filecheck = False
        for l in lines[0:30]:
            filetest = re.search(reREFERENCE, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als getdatacsv-file. Verkeerde filetype??'

        stat = dict()
        meta = {}
        x = 0
        #METADATA
        #print(lines)
        #try:

        decode_metainfo = r'".+=(.+)"'
        while int(lines[x].find('(m,n)')) == -1:
            #while int(lines[x].find('(m,')) == -1:
            #print(lines[x])
            print('\t'+lines[x])
            if "Reference date" in lines[x]:
                itdate = re.search(decode_metainfo, lines[x]).groups()[0]
                itdate = itdate.strip()
                #itdate = lines[x][48:59]
                meta.update({'itdate':itdate})
            elif "SDS-file" in lines[x]:
                sds = re.match(decode_metainfo, lines[x]).groups()[0]
                sds = sds.strip()
                #sds = lines[x][19:59]
                meta.update({'filename':sds})
            elif "Time zone" in lines[x]:
                timezone = re.match(decode_metainfo, lines[x]).groups()[0]
                timezone = timezone.strip()
                #timezone = lines[x][19:59]
                meta.update({'timezone':timezone})
            elif "Unit" in lines[x]:
                unit = re.match(decode_metainfo, lines[x]).groups()[0]
                unit = unit.strip()
                #unit = lines[x][19:23]
                meta.update({'unit':unit})
            elif "Layer" in lines[x]:
                layer = re.match(decode_metainfo, lines[x]).groups()[0]
                layer = layer.strip()
                #layer = int(lines[x][19:29])
                meta.update({'layer':layer})
            elif "Constituent" in lines[x]:
                const = re.match(decode_metainfo, lines[x]).groups()[0]
                const = layer.strip()
                #const = lines[x][19:29]
                meta.update({'constituent':const})
            elif "Constituent name" in lines[x]:
                constname = re.search(decode_metainfo, lines[x]).groups()[0]
                constname = constname.strip()
                #constname = lines[x][19:29]
                meta.update({'constituentname':constname})
            elif "Constituent unit" in lines[x]:
                constunit = re.search(decode_metainfo, lines[x]).groups()[0]
                constunit = constunit.strip()
                meta.update({'constituentunit':constunit})
            x = x+1#trash = file.readline(g)
        #except:
        #    print(meta)
        #    return x,lines
        #print('\t'+str(meta))
        #stat['meta'] = {'unit':unit, 'itdate':itdate}
        stat['meta'] = meta

        #PUNT
        a = 0
        while int(lines[x].find('#')) == -1:
            name = lines[x][52:].strip().strip('\"')
            try:
                if name in stat:
                    #print('\t'+name+ ' bestaat al')
                    name = 'temp'+str(a)
                temp = re.search(r'.*?\(\s*(\d+),\s*(\d+)\).*\(x, y\)=\(\s*(\d+\.\d*),(\d+\.\d*)\)\s*(\w+)', lines[x])
                stat[name] = {'m':int(temp.groups()[0]), 'n':int(temp.groups()[1]), \
                    'x':float(temp.groups()[2]), 'y':float(temp.groups()[3]), \
                    'ColNR':int(a)}
                #stat[name] = {'m':int(lines[x][8:13]) , 'n':int(lines[x][15:18]), \
                #    'x':float(lines[x][29:38]), 'y':float(lines[x][40:49]), \
                #    'ColNR':int(a)}
            except:
                #print(lines[x])
                stat[name] = {'m':int(lines[x][9:13]), 'n':int(lines[x][15:19]), \
                    'x':float(lines[x][30:39]), 'y':float(lines[x][41:50]), \
                    'ColNR':int(a)}
            a = a+1
            x = x+1#trash = file.readline(g)

        x = x+2
        data = np.empty(shape=[len(lines)-x, len(stat)-1])
        tijd = np.empty(shape=len(lines)-x)
        a = 0
        #print('ggrrrrr')
        while x != len(lines):
            test = checkcommentline(lines[x])
            if test is True:
                x = x+1
                continue

            lijn = lines[x].strip().split(',') #splitsen per locatie en new line verwijderen
            #print(lijn)
            #tijd[a] = np.float32(lijn[0])
            #data[a, :] = np.float32(lijn[1:])
            tijd[a] = np.array(lijn[0], dtype=float)
            #data[a, :] = np.float32(lijn[1:], dtype=float)
            data[a, :] = np.array(lijn[1:], dtype=float)

            x = x+1
            a = a+1
        #del(lines)
        gc.collect() # garbage collection
        #data = np.array(datalist)

        tijdmin = tijd
        tijd = convDT(tijd, stat['meta']['itdate'])

        return stat, tijd, data, tijdmin

    @staticmethod
    def getdatacsv_barrier(filename, pad=os.getcwd()):

        reREFERENCE = r'\s*\"Reference date\s* = '
        print(color_scheme.startinlezencoloring+\
        'inlezen getdata-csv bestand'+\
        color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        #Check bestand
        filecheck = False
        for l in lines[0:30]:
            filetest = re.search(reREFERENCE, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als getdatacsv-file. Verkeerde filetype??'

        stat = dict()
        meta = {}
        x = 0
        #print('\t'+lines[x])

        decode_metainfo = r'".+ = (.+)"'
        while int(lines[x].find('(m, n)')) == -1:
            #print('\t'+lines[x])
            if "Reference date" in lines[x]:
                itdate = re.search(decode_metainfo, lines[x]).groups()[0]
                itdate = itdate.strip()
                #itdate = lines[x][48:59]
                meta.update({'itdate':itdate})
            elif "SDS-file" in lines[x]:
                sds = re.match(decode_metainfo, lines[x]).groups()[0]
                sds = sds.strip()
                #sds = lines[x][19:59]
                meta.update({'filename':sds})
            elif "Time zone" in lines[x]:
                timezone = re.match(decode_metainfo, lines[x]).groups()[0]
                timezone = timezone.strip()
                #timezone = lines[x][19:59]
                meta.update({'timezone':timezone})
            elif "Unit" in lines[x]:
                unit = re.match(decode_metainfo, lines[x]).groups()[0]
                unit = unit.strip()
                #unit = lines[x][19:23]
                meta.update({'unit':unit})
            x = x+1

        stat['meta'] = meta

        temp = re.search(r'.*?\(\s*(\d+),\s*(\d+)\).*\(x,y\)=\(\s*(\d+\.\d*),(\d+\.\d*)\)\s*(\w+\s*(\w*\s*)+)', lines[x])
        name = temp.groups()[4]

        #stat[name] = {'m':int(temp.groups()[0]) , 'n':int(temp.groups()[1]), \
        #    'x':float(temp.groups()[2]), 'y':float(temp.groups()[3]), \
        #    'barriername':temp.groups()[4]}

        if True:
            x = x+2
            parameters = lines[x].split(', ')[1:]
            a = 0
            for p in parameters:
                name = p.strip()[1:-1].upper()
                stat[name] = {'m':int(temp.groups()[0]), 'n':int(temp.groups()[1]), \
                    'x':float(temp.groups()[2]), 'y':float(temp.groups()[3]), \
                    'barriername':temp.groups()[4], 'ColNR':a}
                a = a+1

            x = x+1
            data = np.empty(shape=[len(lines)-x, len(parameters)])
            tijd = np.empty(shape=len(lines)-x)
            a = 0

            while x != len(lines):
                test = checkcommentline(lines[x])
                if test is True:

                    x = x+1
                    continue

                lijn = lines[x].strip().split(',') #splitsen per locatie en new line verwijderen
                #tijd[a] = np.float32(lijn[0])
                #data[a, :] = np.float32(lijn[1:])

                tijd[a] = np.array(lijn[0], dtype=float)
                #data[a, :] = np.float32(lijn[1:], dtype=float)
                data[a, :] = np.array(lijn[1:], dtype=float)

                x = x+1
                a = a+1
            #del(lines)
            gc.collect() # garbage collection
            #data = np.array(datalist)
            tijd = convDT(tijd, stat['meta']['itdate'])
        return stat, tijd, data

    @staticmethod
    def timeseries_regular(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+\
        r'inlezen \'regular timeseries\' '+\
        color_scheme.endcoloring)
        import time

        #Controle filetype
        padfile = os.path.join(pad, filename)
        g = open(padfile, 'r')#error handling

        text = g.read()
        g.close()

        assert (re.search(r'\'regular', text, re.M|re.I)), \
               "Dit is geen file met regelmatige (regular) tijdserie"
        #x = re.search('\'regular', text, re.M|re.I)
        #if x is None:
        #    raise TypeError('Dit is geen file met regelmatige (regular) tijdserie')

        #daadwerkelijke inlezen
        lines = _asciiinlezen(pad, filename)

        #x = 0
        P = []
        T = []
        data = []
        stap = 1
        temp = None

        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue

            if stap == 1:
                #REGEL (T)S:
                if temp is None:
                    #print('stap 1')
                    temp = re.match(r'\s*#', l, re.I) # constituent

                    if temp is None:
                        temp = re.search(r'\s*T?S.*:.*P\s*(\d+)', l, re.I) # constituent

                        if temp != None:
                            ptemp = temp.group(1)

                            #t1 = time.time()
                            P.append(int(ptemp))
                            stap = 2
                    else:
                        temp = None

            elif stap == 2:
                #REGEL FRAME
                #print('stap 2')

                temp = re.search(r'\s*FR\D*(\d+.?\d*)\D*(\d+.?\d*)\D*(\d+.?\d*)', l, re.I)
                if temp != None:
                    tstart, tint, tstop = temp.groups()
                    ttemp = np.arange(float(tstart), float(tstop)+1, float(tint))
                    T.append(ttemp)
                    data.append(np.zeros([ttemp.size], dtype='float'))
                    stap = 3

            elif stap == 3:
                #print('stap 3')

                #REGEL VALUES, met eventueel data
                temp = re.search(r'\s*VA*', l, flags=re.I)
                if temp != None:
                    j = re.split(r'\s+|=', l.strip())
                    # regels data

                    c = 0

                    if len(j) > 2: #and j[-1] != '':
                        #toevoegen van een array aan [data]
                        print(j)
                        print(l)
                        val = np.array(j[1:], dtype=np.float)
                        data[len(P)-1][c:c+val.size] = val
                        c += len(j)-1
                    stap = 4
                #print('stap 4')

            elif stap == 4:
                #REGELS DATA
                if c < ttemp.size:
                    try:
                        val = np.array(l.strip().split(), dtype='float')
                    except:
                        # regels met een hashtag?
                        temp = re.match(r'\s*#*([^#]+)', l).groups()[0]
                        val = np.array(temp.strip().split(), dtype='float')
                    try:
                        #print(len(P))
                        #print(val.size)
                        #print(c)
                        data[len(P)-1][c:c+val.size] = val
                    except:
                        print(len(P))
                        raise
                        #return data, c, val
                    c += val.size
                else:
                    stap = 1
                    #print('stap 1')

                    temp = re.search(r'\s*T*S.*:.*P\s*(\d+)', l, re.I)
                    if temp is None:
                        temp = re.search(r'\s*S.*:.*P\s*(\d+)', l, re.I) #hydraulica
                    if temp != None:
                        ptemp = temp.group(1)
                        t1 = time.time()
                        P.append(int(ptemp))
                        stap = 2
                        #print('stap 2')

        return P, T, data

    @staticmethod
    def timeseries_irregular(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+\
        r'inlezen \'IRregular timeseries\' '+\
        color_scheme.endcoloring)
        import time

        padfile = os.path.join(pad, filename)
        g = open(padfile, 'r')    #error handling

        text = g.read()
        g.close()

        x = re.search(r'\'irregular', text, re.M|re.I)
        if x is None:
            x = re.search('TIME_and_WINDVALUES', text, re.M|re.I)
            if x is None:
                raise TypeError('Dit is geen file met onregelmatige (irregular) tijdserie: \
                                gebruik timeseries_regular? ')
            else:
                raise TypeError('Dit is een windfile: gebruik timeseries_irregular_wind')

        #daadwerkelijke inlezen
        lines = _asciiinlezen(pad, filename)
        x = 0
        P = []
        T = []
        data = []
        stap = 1
        datatemp = []
        Ttemp = []
        temp = None
        for l in lines:
            test = checkcommentline(l)
            if test is True:
                continue

            if stap == 1:
                #print('stap 1')
                #REGEL (T)S:
                if temp is None:
                    temp = re.search(r'\s*T*S.*:.*P\s*(\d+)', l, re.I) # constituent

                    if temp is None:
                        temp = re.search(r'\s*S.*:.*P\s*(\d+)', l, re.I) #hydraulica
                if temp != None:
                    #print('stap 1')

                    ptemp = temp.group(1)

                    #t1 = time.time()
                    P.append(int(ptemp))
                    if len(datatemp) != 0:
                        data.append(datatemp)
                        T.append(Ttemp)
                        Ttemp = []
                        datatemp = []
                    stap = 2

            elif stap == 2:
                print('stap 2')
                print(l)
                #REGEL VALUES, met eventueel data
                temp = re.search(r'\s*TIME_AND*', l, flags=re.I)
                if temp is not None:
                    #temp = re.match(r'.+=\s*(\d+)\s*(\d{1, 2}):(\d{2})\s*(.*)', l)
                    temp = re.match(r'.+=\s*\(*(\d+)\s*(\d{1,2}):(\d{2})\)*\s*\)*(.*)', l)
                    if temp is None:
                        temp = re.match(r'.+=\s*\(*(\d+)\s*(\d{1, 2})\s*(\d{1, 2})\)*\s*\)*(.*)', l)
                        if temp is None:
                            raise TypeError('help')

                    # regels data


                    datatemp.append(temp.groups()[3])
                    Ttemp.append(int(temp.groups()[0])*1440+int(temp.groups()[1])*60+int(temp.groups()[2]))

                else:
                    temp = re.search(r'\s*T*S.*:.*P\s*(\d+)', l, re.I)
                    if temp is None:
                        temp = re.search(r'\s*S.*:.*P\s*(\d+)', l, re.I) #hydraulica
                    if temp != None:
                        #print('stap 1')
                        ptemp = temp.group(1)

                        t1 = time.time()
                        P.append(int(ptemp))
                        if len(datatemp) != 0:
                            data.append(np.array(datatemp, dtype='float32'))
                            T.append(np.array(Ttemp))
                            Ttemp = []
                            datatemp = []
                        stap = 2
                        #print('stap 2')
        if len(datatemp) != 0:
            data.append(np.array(datatemp, dtype='float32'))
            T.append(np.array(Ttemp))
        return P, T, data

    @staticmethod
    def timeseries_irregular_wind(filename, pad=os.getcwd()):
        padfile = os.path.join(pad, filename)
        g = open(padfile, 'r')    #error handling

        text = g.read()
        g.close()
        assert re.search('TIME_and_WINDVALUES', text, re.M|re.I), 'Niet herkend als wind file'
        g.close()
        print(color_scheme.startinlezencoloring+\
        r'inlezen \'IRregular timeseries_wind\' '+\
        color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)
        #x = 0
        #P = []
        T = []
        data = []

        #stap = 1
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue

            temp = re.search(r'\s*TIME_AND*', l, flags=re.I)
            if temp != None:
                temp = re.match(r'.+=\s*(\d+)\s*(\d{1, 2}):\s*(\d{1, 2})\s*(\d+.?\d*)?\s+(\d+.?\d*)?', l)
                # regels data

                try:
                    data.append([temp.groups()[3], temp.groups()[4]])
                except:
                    print(l)
                T.append(int(temp.groups()[0])*1440+int(temp.groups()[1])*60+int(temp.groups()[2]))
        if len(data) != 0:
            data = np.array(data, dtype='float32')
            T = np.array(T)
        return T, data

    @staticmethod
    def adobs(filename, pad=os.getcwd()):
        import datetime
        lines = _asciiinlezen(pad, filename)

        filecheck = False
        for l in lines[0:20]:
            filetest = re.search('station', l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als adobs-file. Verkeerde filetype??'

        #Stap 1 meta data inlezen

        adobs_keywords1 = [{'station':['name']}, \
            {'coor':['zpos', 'zref', 'system', 'm', 'n']}, \
            {'time':['zone', 'offset']}, \
            {'values':['dummy', 'unit']}]
        x1 = 0
        x2 = 0
        adobs_meta = {}
        metainfo_stop = False

        for k1 in adobs_keywords1:
            #print(r'\t'+k1.keys()[0])
            temp = None
            while temp is None:
                temp = re.search(k1.keys()[0], lines[x1].lower())
                if temp != None:
                    x2 = x1
                    adobs_keywords2 = k1.values()[0]
                    for k2 in adobs_keywords2:
                        #print(r'\t'+k2)
                        temp = None
                        while temp is None:
                            temp = re.search(r'[\A\s]'+k2+r'\s*=\s*(\S+)', lines[x2].lower())
                            #adobs file maakt gebruik van default waarde
                            if re.search('data', lines[x2].lower()) != None:
                                metainfo_stop = True
                                break
                            if temp != None:
                                adobs_meta.update({k2:temp.groups()[0].upper()})
                            else:
                                x2 = x2+1
                        if metainfo_stop is True:
                            break
                    x1 = x2

                else:
                    if metainfo_stop is True:
                        break
                    x1 = x1+1
                x2 = x1

        #Stap2 inlezen data
        x = 0
        while re.search('data', lines[x].lower()) is None:
            x = x+1
        while re.match(r'\s*\d+\s+\d+\s+-*\d+', lines[x]) is None:
            x = x+1

        test = lines[x].split()
        data = np.zeros(shape=[len(lines)-x, len(test)-2])
        T = np.array([])
        for a in range(x, len(lines)):
            test = checkcommentline(lines[a])
            if test is True:

                continue

            D = lines[a].split()
            t = D[0]+' '+D[1].rjust(6, '0')
            T = np.append(T, datetime.datetime.strptime(t, '%Y%m%d %H%M%S'))

            for b in range(0, len(D)-2):
                data[a-x, b] = float(D[b+2])
        data = data.flatten()

        return adobs_meta, T, data
        #inlezen tijdreeks data

class lijn(object):
    """ element dat uit een begin en een eindpunt bestaat en een lijnelement daartussen"""
    @staticmethod
    def opening(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen opening'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        reOPEN = r'\s*OPEN\s*'+3*r'(\d+).*?'+r'\'(.+)\''

        filecheck = False
        for l in lines:
            filetest = re.search(reOPEN, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als opening-file. Verkeerde filetype??'

        opening = {}
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            #temp = re.match(COMMENTLINE, l)
            #if temp != None:
            #    continue # regel uitgecomment

            temp = re.match(r'\s*OPEN\s*'+3*r'(\d+).*?'+r'\'(.+)\'', l, re.I)
            if temp != None:
                t = temp.groups()
                opening[int(t[0])] = {'P1':int(t[1]), 'P2':int(t[2]), 'name':t[3].upper()}

        return opening

    @staticmethod
    def boundary(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen boundary'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        #reB = '\s*B\s*:\s*OPEN\s*(\d+).*?\'(.+?)\'.+?\'(.+?)\'.+? = (.+)'

        #filecheck = False
        #for l in lines:
        #    filetest = re.search(reB, l, re.I)
        #    if filetest != None:
        #        filecheck = True
        #assert filecheck, 'Niet herkend als boundary-file. Verkeerde filetype??'

        boundaries = {}
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            #temp = re.match(r'\s*#', l)

            #temp = re.match(COMMENTLINE, l)
            #if temp != None:
            #    continue #uitgecomment

            temp = re.match(r'\s*B\s*:\s*OPEN\s*(\d+).*?\'(.+?)\'.+?\'(.+?)\'.+?=(.+)', l, re.I)

            if temp != None:
                t = temp.groups()
                if t[3].lower().find('same') < 0:
                    boundaries[int(t[0])] = {'btype':t[1], \
                               'bdef':t[2], \
                               'refl':t[3], \
                               'same':False}
                else:

                    boundaries[int(t[0])] = {'btype':t[1], \
                               'bdef':t[2], \
                               'refl':t[3].split()[0], \
                               'same':True}
        return boundaries

    @staticmethod
    def closeuv(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen schotjes'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        reMNN = r'\s*MNN'
        reNMM = r'\s*MNN'
        filecheck = False
        for l in lines:
            filetest = re.search(reMNN, l, re.I)
            if filetest != None:
                filetest = re.search(reNMM, l, re.I)
                if filetest != None:
                    filecheck = True
            else:

                filecheck = True
        assert filecheck, 'Niet herkend als closeuv-file. Verkeerde filetype??'

        closeuv = []#closev = []
        a = 0
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            if re.match(r'\s*MNN', l, re.I) != None:

                temp = re.match(r'.+?\(?.*?(\d+).+?(\d+).+?(\d+)\)*', l)
                t = temp.groups()
                L1 = [int(t[0]), int(t[1])]
                L2 = [int(t[0]), int(t[2])]
                closeuv.append({'L1':L1, 'L2':L2, 'utype':1, 'vtype':0})

            elif re.match(r'\s*NMM', l, re.I) != None:
                temp = re.match(r'.+?\(?.*?(\d+).+?(\d+).+?(\d+)\)*', l)
                t = temp.groups()
                L1 = [int(t[1]), int(t[0])]
                L2 = [int(t[2]), int(t[0])]
                closeuv.append({'L1':L1, 'L2':L2, 'utype':0, 'vtype':2})
            a = a+1
        return closeuv

    @staticmethod
    def barrier(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen barriers'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        reBC = r'\s*B\s*(\d+).+?C\s*(\d+)'
        reBP = r'\s*B\s*(\d+).*?P\s*(\d+).+?\'(.+?)\''
        filecheck = False
        for l in lines:
            filetest = re.search(reBC, l, re.I)
            if filetest != None:
                filetest = re.search(reBP, l, re.I)
                if filetest != None:
                    filecheck = True
            else:

                filecheck = True
        assert filecheck, 'Niet herkend als barrier-file. Verkeerde filetype??'

        barrier = {}
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            #temp = re.match(COMMENTLINE, l)
            #    if temp != None:
            #        continue#uitgecomment

            temp = re.match(r'\s*B\s*(\d+).+?C\s*(\d+)', l, re.I)
            if temp != None:
                #gedefinieerd als curve
                nr = temp.groups()[0]
                barrier[nr] = {'C':int(temp.groups()[1]), 'utype':'c', 'vtype':'c', 'name':nr}
                #barrier.append({'C':int(temp.groups()[1]), 'utype':'c', 'vtype':'c', nr':nr})
            else:
                #gedefinieerd als punt
                temp = re.match(r'\s*B\s*(\d+).*?P\s*(\d+).+?\'(.+?)\'', l, re.I)
                if temp != None:
                    nr = int(temp.groups()[0])
                    if temp.groups()[2][0] == 'r':
                        utype = 1
                        vtype = 0
                    else:
                        utype = 0
                        vtype = 2
                    barrier[nr] = {'P1':int(temp.groups()[1]), \
                           'P2':int(temp.groups()[1]), \
                           'utype':utype, \
                           'vtype':vtype, \
                           'name':nr}
        return barrier

    @staticmethod
    def curve(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen curves'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        reC = r'\s*C\s*(\d+).+?P\s*(\d+).+?P\s*(\d+).+\'(.+)?\''
        filecheck = False
        for l in lines:
            filetest = re.search(reC, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als curve-file. Verkeerde filetype??'

        curve = {}
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            #temp = re.match(COMMENTLINE, l)
            #if temp != None:
            #    continue #uitgecomment
            temp = re.match(r'\s*C\s*(\d+).+?P\s*(\d+).+?P\s*(\d+).+\'(.+)?\'', l, re.I)

            #if temp is None:
            #    continue #uitgecomment

            #else:
            t = temp.groups()
            curve[int(t[0])] = {'P1':int(t[1]), 'P2':int(t[2]), 'name':t[3].upper()}
        return curve

    @staticmethod
    def checkcurve(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen check-curves'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)
        checkc = []
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            #temp = re.match(COMMENTLINE, l)
            #if temp != None:
            #    continue #uitgecomment

            temp = re.match(r'[^#]*', l)
            l_zcomm = temp.group()
            temp = re.findall(r'C\s*(\d+)', l_zcomm, re.I)
            if len(temp) != 0:
                for t in temp:
                    checkc.append(int(t))
        return checkc

class route(object):
    """ element dat uit een begin en een eindpunt bestaat.
    En met meerdere tussenpunten en lijnelementen die de punten met elkaar verbinden."""
    def __init__(self):
        from matplotlib.path import Path
        self.Path = Path


    def lines(self, filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen outline'+color_scheme.endcoloring)
        """ lijnstukken die in siminp onder keyword LINES vallen"""
        lines = _asciiinlezen(pad, filename)

        reLCOOR = r'\s*(L\s*:).+(COOR=)'
        filecheck = False
        for l in lines:
            filetest = re.search(reLCOOR, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als lines-file. Verkeerde filetype??'

        outl = []
        stap = 1
        XY = []
        #X = [];Y = [];#a = 0
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue

            if stap == 3:
                #temp = re.search(r'\.*(\d+(\.\d*)?|\.d+).+?(\d+)', l)
                temp = re.search(r'\s*(\d+)\.*\d*\s+(\d+)?', l)
                if temp != None:
                    XY.append([float(temp.group(1)), float(temp.group(2))])
                else:
                    #print(X, Y        #outl.append(np.array([np.array(X), np.array(Y)])))
                    outl.append(self.Path(np.array(XY)))
                    XY = []
                    stap = 1
            if stap == 1:
                temp = re.search(r'\s*(L\s*:).+(COOR=)', l, re.M|re.I)
                if temp != None:
                    if len(temp.groups()) == 2:
                        if temp.groups()[1] == 'COOR=':
                            stap = 3 # ga rechtstreeks naar inlezen van de lijn
                        else:
                            raise Exception
                    else:
                        stap = 2
            if stap == 2:
                temp = re.search(r'\.*COOR=', l, re.M|re.I)
                if temp != None:
                    stap = 3
        outl.append(self.Path(np.array(XY)))    #outl.append(Path([X, Y]))
        return outl

    @staticmethod
    def enclosure(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen enclosure'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        reENCL = r'E\s*'
        filecheck = False
        for l in lines:
            filetest = re.search(reENCL, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als enclosure-file. Verkeerde filetype??'

        encl = []
        mn_lijn = []
        for l in lines:
            #regel identifier E: Enclosure = nieuw lijnstuk
            test = checkcommentline(l)
            if test is True:
                continue

            temp = re.match(r'\s*E', l, re.I)
            if temp != None:
                if mn_lijn != []:
                    encl.append(np.array(mn_lijn))
                    mn_lijn = []
            else:
                temp1 = re.match(r'\s*(\d+)\s+(\d+)\s*#?.*?$', l)
                temp2 = re.match(r'\s*\(', l)
                ##regels mn coordinaten

                if temp1 != None:
                    temp4 = re.match(r'\s*(\d+)\s+(\d+)', l)
                    m, n = temp4.groups()
                    mn_lijn.append([int(m), int(n)])

                elif temp2 != None:
                    temp3 = re.split(r'\(|\)', l)
                    for t in temp3:
                        t = t.strip()
                        if t != '' and t != ', ':
                            mn = t.split(',')
                            mn_lijn.append([int(mn[0]), int(mn[1])])

        encl.append(np.array(mn_lijn))
        return encl

class punt(object):
    @staticmethod
    def point(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen points'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        reP = r'\s*P\s*'+3*r'(\d+).*?'

        filecheck = False
        for l in lines:
            filetest = re.search(reP, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als point-file. Verkeerde filetype??'

        punt = {}
        x = 0
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue

            temp1 = re.match(r'.+?\'.+?\'.+?\'.+?\'', l)
            if temp1 != None:
                while x == 0:
                    #print('\t'+ l+ '.......\n')
                    x = x+1
                #print('2 punten op lijn, met naam')
                #temp2 = re.match('\s*P\s*(\d+).*?(\d+).*?(\d+).*?\'(.+)\'.+?P\s*(\d+).*?(\d+).*?(\d+).*?\'(.+)\'', l, re.I)
                temp2 = re.match(r'\s*P\s*'+3*r'(\d+).*?'+r'\'(.+)\'.+?P\s*'+3*r'(\d+).*?'+r'\'(.+)\'', l, re.I)
                t = temp2.groups()
                punt[int(t[0])] = {'m':int(t[1]), 'n':int(t[2]), 'name':t[3].upper()}
                punt[int(t[4])] = {'m':int(t[5]), 'n':int(t[6]), 'name':t[7].upper()}
            else:
                temp1 = re.match(r'.+?\'.+?\'', l)
                if temp1 != None:
                    #print('1 punt op lijn met naam')
                    #temp2 = re.match('\s*P\s*(\d+).*?(\d+).*?(\d+).*?\'(.+)\'', l, re.I)
                    temp2 = re.match(r'\s*P\s*'+3*r'(\d+).*?'+r'\'(.+)\'', l, re.I)

                    t = temp2.groups()
                    punt[int(t[0])] = {'m':int(t[1]), 'n':int(t[2]), 'name':t[3].upper()}
                else:
                    #
                    #temp1 = re.match('\s*P.+?\).+?P', l, re.I)
                    temp1 = re.match(r'\s*P.+?\).+?P.+?\)', l, re.I)
                    if temp1 != None:
                        #print('twee punten op een lijn zonder naam ')
                        temp2 = re.match(r'\s*P\s*(\d+).*?(\d+).*?(\d+).+?P\s*(\d+).*?(\d+).*?(\d+)', l, re.I)
                        t = temp2.groups()
                        punt[int(t[0])] = {'m':int(t[1]), 'n':int(t[2]), 'name':None}
                        punt[int(t[3])] = {'m':int(t[4]), 'n':int(t[5]), 'name':None}
                    else:
                        #print('een punt op lijn zonder naam')
                        temp2 = re.match(r'\s*P\s*(\d+).*?(\d+).*?(\d+)', l, re.I)
                        t = temp2.groups()
                        punt[int(t[0])] = {'m':int(t[1]), 'n':int(t[2]), 'name':None}
        return punt

    @staticmethod
    def checkpoint(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen check-points'+color_scheme.endcoloring)
        #uitvoerpunten
        lines = _asciiinlezen(pad, filename)
        checkp = []
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            #temp = re.match(COMMENTLINE, l)
            #if temp != None:
            #    continue #uitgecomment

            temp = re.match(r'[^#]*', l)
            l_zcomm = temp.group()
            temp = re.findall(r'P\s*(\d+)', l_zcomm, re.I)
            if len(temp) != 0:
                for t in temp:
                    checkp.append(int(t))
        return checkp

    @staticmethod
    def dam(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+'inlezen dammen'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        reD = r'(\d+)\D+(\d+)'
        filecheck = False
        for l in lines:
            filetest = re.search(reD, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als dam-file. Verkeerde filetype??'

        dampoint = []
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            #temp = re.match(COMMENTLINE, l)
            #if temp != None:
            #    continue #uitgecomment

            temp = re.match(r'(.+)#?', l).group()
            temp2 = re.split(r'\(|\)', temp)
            for t in temp2:
                temp3 = re.match(r'(\d+)\D+(\d+)', t)
                if temp3 != None:
                    dampoint.append([int(temp3.groups()[0]), int(temp3.groups()[1])])
        return np.array(dampoint)

    @staticmethod
    def overlaat(filename, pad=os.getcwd(), mnminmax=[0, 0, np.inf, np.inf]):
        """inlezen van een overlaat
        uitvoer: overlaat = > dictionary
        dict : L1 => list: [int (m-coordinaat), int (n-coordinaat)]
               utype/vtype

               u_o/v_o        overflow height
               u_sd/v_sd    sill down
               u_su/v_su    sill up
               u_g/v_g        groyne

        """
        print(color_scheme.startinlezencoloring+'inlezen overlaten'+color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)

        reW = r'\s*W\s*:?[^\']+?(\'.+)'
        filecheck = False
        for l in lines:
            filetest = re.search(reW, l, re.I)
            if filetest != None:
                filecheck = True
        assert filecheck, r'Niet herkend als weir-file. Verkeerde filetype??'

        overlaat = []
         #test

        for l in lines:
            test = checkcommentline(l)

            if test is True:

                continue
            else:
                temp1 = re.match(r'\s*W\s*:?\s*([^\']+)?', l).group(1)
                t = temp1.split()
                if int(t[0]) > mnminmax[0] and \
                int(t[1]) > mnminmax[1] and \
                int(t[0]) < mnminmax[2] and \
                int(t[1]) < mnminmax[3]:
                    #u_o = np.float32(t[2])
                    #u_su = np.float32(t[3])
                    #u_sd = np.float32(t[4])
                    #v_o = np.float32(t[5])
                    #v_su = np.float32(t[6])
                    #v_sd = np.float32(t[7])
                    u_o = float(t[2])
                    u_su = float(t[3])
                    u_sd = float(t[4])
                    v_o = float(t[5])
                    v_su = float(t[6])
                    v_sd = float(t[7])

                    temp2 = re.match(r'\s*W\s*:?[^\']+?(\'.+)', l).group(1)
                    temp3 = temp2.split('\'')
                    u_g = str(temp3[1])
                    v_g = str(temp3[3])
                    temp4 = temp3[-1].split()
                    utype = int(temp4[0])
                    vtype = int(temp4[1])

                else:
                    continue

                re_overlaatext = re.match(r'.*\'\s+(\d+.*)', l)
                #print(l)
                splitresults = re_overlaatext.group(1).split()
                if len(splitresults) > 2:
                    #[ucrl = None;utalu = None;utald = None;vtalu = None;vtald = None;
                    #veg = None;cd1 = None;cd2 = None;vttype = None
                    #return splitresults
                    values = 12*[None]

                    for a in range(2, len(splitresults)):
                        if a < 8:
                            values[a] = np.float(splitresults[a])
                        else:
                            if a == 8:
                                values[8] = np.int(splitresults[8])
                            elif a == 11:
                                values[11] = splitresults[11]
                            else:
                                values[a] = np.float(splitresults[a])
                    overlaat.append(
                        {'L1':[int(t[0]), int(t[1])],
                         'u_o':u_o, 'v_o':v_o,
                         'u_sd':u_sd, 'v_sd':v_sd, 'u_sr':u_su, 'v_sr':v_su,
                         'u_g':u_g, 'v_g':v_g,
                         'utype':utype, 'vtype':vtype,
                         'u_cl':values[2], 'u_tr':values[3], 'u_td':values[4],
                         'v_cl':values[5], 'v_tr':values[6], 'v_td':values[7],
                         'veg':values[8], 'cd1':values[9], 'cd2':values[10], 'vttype':values[11]}
                        )
                else:
                    overlaat.append(
                        {'L1':[int(t[0]), int(t[1])],
                         'u_o':u_o, 'v_o':v_o,
                         'u_sd':u_sd, 'v_sd':v_sd, 'u_sr':u_su, 'v_sr':v_su,
                         'u_g':u_g, 'v_g':v_g,
                         'utype':utype, 'vtype':vtype})

        return overlaat

    @staticmethod
    def ruwheidarea(filename, pad=os.getcwd()):
        print(color_scheme.startinlezencoloring+\
        'inlezen ruwheid, nog niet gereed.....'+\
        color_scheme.endcoloring)
        lines = _asciiinlezen(pad, filename)
        reArea = r'^\s*(\d+)'+r'\s*(\d*\.?\d*)\s*'
        filecheck = False
        for l in lines:
            filetest = re.match(reArea, l, re.I)#match!!
            if filetest != None:
                filecheck = True
        assert filecheck, 'Niet herkend als overlaat-file. Verkeerde filetype??'

        ruwheid = []
        for l in lines:
            test = checkcommentline(l)
            if test is True:

                continue
            try:
                #temp1 = re.match('\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d*\.?\d*)', l).groups()
                temp1 = re.match(3*r'\s*(\d+)'+r'\s*(\d*\.?\d*)', l).groups()
            except:
                return l
            ruwheid.append({\
                            'L1':[int(temp1[1]), int(temp1[0])], \
                            'roughcode':int(temp1[2]), \
                            'fraction':float(temp1[3])})
        return ruwheid
