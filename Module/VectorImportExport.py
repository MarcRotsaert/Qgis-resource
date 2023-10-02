

""" Your Description of the script goes here """
# 2015-2016 MRO

# Some commonly used imports

#from qgis.core import *
#from qgis.core import QgsVectorLayer,QgsMapLayerRegistry,QgsCoordinateReferenceSystem,QgsVectorFileWriter, NULL
from qgis.core import QgsVectorLayer,QgsProject,QgsCoordinateReferenceSystem,QgsVectorFileWriter, NULL
#from PyQt4.QtCore import *
import os
import numpy as np
import processing

TEMPDIR_WIN_1='D:/temp'
TEMPDIR_WIN_2='C:/TEMP'
TEMPDIR_LINUX=os.path.expanduser("~")#Bijvoorbeeld '/home/svasekz/mro'
wkt_ext='dat'
wktfield='geom'

def checkpad(pad):
    padresult = os.path.exists(pad)
    if padresult==False:
        print(pad +': Pad bestaat niet')
    return padresult

class VectorImportExport:
    def preprocessImport(self,Data,param=None):
        import vector
        assert type(Data)==dict
        Dictio={}
        if isinstance(param,str):
            param=[param]
        elif param==None:
            param=self.Flowparam
        elif type(param)!=list:
            raise TypeError#, 'ongeldige invoer voor type '

        for p in param:
            if p.lower()=='vel':
                print('Cart')
                Cart=vector.Cart(Data['U'],Data['V'],ric='GT')
                vel,degn=Cart.cart2naut()
                if type(vel)!=np.ma.MaskedArray:
                    vel=np.ma.MaskedArray(vel,mask=False)
                    degn=np.ma.MaskedArray(degn,mask=False)
                Dictio['vel']=vel;Dictio['degn']=degn
            else:
                data=Data[p]
                if type(data)!=np.ma.MaskedArray:
                    data=np.ma.MaskedArray(data,mask=False)
                Dictio[p]=data
        return Dictio

    def getTempdir(self):
        """ TEMP-directory: helpfunctie om (tussen)resultaten op te slaan"""
        if os.name=='nt':
            if os.path.exists(TEMPDIR_WIN_1):
                self.TEMPDIR=TEMPDIR_WIN_1
            elif os.path.exists(TEMPDIR_WIN_2):
                self.TEMPDIR=TEMPDIR_WIN_2
            else:
                raise 'Inaccurate TEMPDIR'
        else:
            self.TEMPDIR=self.TEMPDIR_LINUX
        return self.TEMPDIR

    def getTempfile(self,ext):
        self.getTempdir()
        ext=ext.strip('.')
        a=1
        while os.path.exists(os.path.join(self.TEMPDIR,'tmp'+str(a)+'.'+ext )):
            a=a+1
        tempfile=os.path.join(self.TEMPDIR,'tmp'+str(a)+'.'+ext )
        return tempfile

    def getFilename(self,file,pad,ext):
        ext=ext.strip('.')
        if file==None:
            file_name=self.getTempfile(ext)
        else:
            file=file.strip('.'+ext)
            if pad==None:
                file_name=file+'.'+ext
            else:
                file_name=os.path.join(pad,file)+'.'+ext

            p,f=os.path.split(file_name)
            if os.path.exists(p)==False:
                print('non -existing pad: '+p)
                raise Exception
        return file_name

    def getFields(self):
        """Haal velden uit een laag, voeg type toe en zet deze in een list """
        fieldobj=self.Layer.fields()
        field=[]
        for fo in fieldobj.toList():
            fn=str(fo.name())
            #print fo.typeName().lower()
            if fo.typeName().lower()=='integer':
                ft='i8'
            elif fo.typeName().lower()=='integer64':
                ft='i8'
            elif fo.typeName().lower()=='string':
                ft='S1'
            elif fo.typeName().lower()=='text':
                ft='S1'
            elif fo.typeName().lower()=='real':
                ft='f8'
            elif fo.typeName().lower()=='double':
                ft='d'
            elif fo.typeName().lower()=='date':
                ft='QDate'
            else:
                raise TypeError#, fo.typeName().lower() +' is non existing' 
            field.append((fn,ft))
        return field
    """
    def reprojectLayer(self,epsg):
        import processing
        self.getTempdir()
        filein=self.getFilename(None,self.TEMPDIR,'shp')
        tempfilein=os.path.join(self.TEMPDIR,filein)
        QgsVectorFileWriter.writeAsVectorFormat(self.Layer,tempfilein,None,None) 
        fileuit=self.getFilename(None,self.TEMPDIR,'shp')
        tempfileuit=os.path.join(self.TEMPDIR,fileuit)
        processing.runalg('qgis:reprojectlayer',tempfilein,'epsg:'+str(epsg),tempfileuit)
        return tempfileuit
    """

    def coor2Dict(self,Fe):
        """Zet coordinaten uit feature in een dictionary"""
        #Line=Fe.geometry().geometry().coordinateSequence()
        Line=Fe.geometry().vertices()
        X=[];Y=[];coordict={}
        for L in Line:
            #Points=L[0][:]
            Points=L.coordinateSequence()[0][0][:]
            for P in Points:
                X.append(P.x())
                Y.append(P.y())
            #if len(Line)>1: #Multiline
            #    X.append(np.nan)
            #    Y.append(np.nan)
        coordict['x']=X;coordict['y']=Y
        return coordict

    def removeTemplayer(self):
        """ """
        tmpnaam='tmp' 
        tdir= self.getTempdir()
        #1) Verwijder laag uit maplayerregistry
        print(tdir)
        print(tmpnaam)
        #for l in QgsMapLayerRegistry.instance().mapLayers().values():
        for l in QgsProject.instance().mapLayers().values():
            if l.source().startswith(os.path.join(tdir,tmpnaam)):
                print(l.id()+' Wordt verwijdert uit Qgis')
                #QgsMapLayerRegistry.instance().removeMapLayer(l.id())
                QgsProject.instance().removeMapLayer(l.id())
        #2) Verwijder tmp bestand uit directory.
        for f in os.listdir(self.getTempdir()):
            if f.startswith( 'tmp.'):
                os.remove(os.path.join(self.getTempdir(),f))
    
    def writeWktpoint(self,arrays,writexyattribuut=False):
        #arrays= dictionary, gevuld met np.array's of een list
        tempfile=self.getFilename(None,None,wkt_ext)
        attributes = arrays.keys()
        if writexyattribuut==False:
            attributes.remove('x')
            attributes.remove('y')

        fid=open(tempfile,'w')
        kopregel='id,geom'
        for v in attributes:
            kopregel=kopregel+','+v
        kopregel = kopregel+'\n'
        fid.write(kopregel)

        form=[];
        for v in attributes:
            checkformat=v[0]
            if type(checkformat)==str:
                form.append('%s')
            else:
                try:
                    checkformat2=checkformat.item()
                except:
                    print('mislukt')
                    checkformat2=checkformat
                print(type(checkformat2))
                if type(checkformat2)==int or type(checkformat2)==np.int32:
                    form.append('%i')
                else:
                    print(checkformat2)
                    form.append('%f')
        m=1
        for a in range(len(arrays['x'])):
            
            if np.isnan(arrays['x'][a]):
                print('nan-waarde in coordinaten: nog een betere oplossing voor verzinnen')
                continue
            fid.write(str(m)+',')
            fid.write('"POINT (')
            fid.write('%f %f)"'% (arrays['x'][a],arrays['y'][a])) 
            x=0
            for v in attributes:#arrays.itervalues():
                fid.write(','+form[x] % (arrays[v][a]))
                x=x+1
            fid.write('\n')
            m=m+1
        fid.close()
        return tempfile

class ExportVector(VectorImportExport):
    """klasse voor het exporteren van laagdata
    invoer: laag
    manier 1) laag = QgsVectorLayer-object ingeladen in qgis, gebruik b.v iface.activeLayer()
    manier 2) laag = string (shape)file , pad = pad naar shapefile.
    """
    def __init__(self,laag,pad=None):
        if pad==None:
            pad=os.getcwd()
        if isinstance(laag,QgsVectorLayer): # laag als VectorLayer-object
            self.Layer=laag
        elif isinstance(laag,str):# laag als filenaam (shape)
            filepad=os.path.join(pad,laag)
            print(filepad)
            self.Layer=QgsVectorLayer(filepad,'temp','ogr')
        else:
            raise TypeError
        try:
            if self.Layer.isValid()==False:
                raise ValueError# 'verkeerd bestandstype?Verkeerde filenaam?Verkeerde directory?'
        except NameError:
            print('Invoer moet Qgis laag zijn, of bestaande vector bestand')

    def exportMat(self,mfile=None,mpad=None):
        """ Schrijf laag weg naar mat-file """
        from matlab import savemat
        file_name=self.getFilename(mfile,mpad,'mat')
        Feat=self.Layer.getFeatures()
        map=np.array(np.zeros(0,))
        x=0
        for Fe in Feat:
            valdict={}
            valdict=self.coor2Dict(Fe)
            for v in self.getFields():
                if Fe[v[0]] != NULL:
                    if v[1]=='QDate':
                        val=Fe[v[0]].toString()
                    else:
                        val=Fe[v[0]]
                        print(val)
                    valdict[v[0]]=val
            if x==0:
                map=np.array(valdict)
            else:
                map=np.append(map,valdict)
            x=x+1
        #return map
        savemat({'qgis':map},file_name)

    def exportKml(self,kfile=None,kpad=None,**kwargs):
        """ Schrijf laag weg naar kml-file 
        Inclusief Optie om ene Namefield en DescriptionField weg te schrijven.
        
            **kwargs-keys 
                NameField
                DescriptionField
                AltitudeMode
                """
        driver="KML"#Voor naamgeving drivers: C:\Program Files (x86)\QGIS 
        kmlfile=self.getFilename(kfile,kpad,'kml')
        if len(kwargs)>0:
            dso_list=[]
            try:
                Name=kwargs['NameField']
                dso_list.append('NameField='+Name)
            except KeyError:
                print('No Namefield defined')
            try:
                Description=kwargs['DescriptionField']
                dso_list.append('DescriptionField='+Description)
            except KeyError:
                print('No DescriptionField defined')
            try:
                print(kwargs['AltitudeMode'])
                Altitudemode=kwargs['AltitudeMode']
                dso_list.append('AltitudeMode='+Altitudemode)
            except KeyError:
                print('No AltitudeModeField defined.....')
            #QgsVectorFileWriter.writeAsVectorFormat(self.Layer,kmlfile,None,None,driver,datasourceOptions=dso_list) 
            QgsVectorFileWriter.writeAsVectorFormat(self.Layer,kmlfile,None,self.Layer.crs(),driver,datasourceOptions=dso_list) 
        else:
            #QgsVectorFileWriter.writeAsVectorFormat(self.Layer,kmlfile,None,None,driver) 
            QgsVectorFileWriter.writeAsVectorFormat(self.Layer,kmlfile,None,self.Layer.crs(),driver) 

    def exportShp(self,sfile=None,spad=None,**kwargs):
        shpfile=self.getFilename(sfile,spad,'shp')
        #print(self.Layer.dataProvider().fields().fieldNameIndex('Descript_2'))
        #print(self.Layer.dataProvider().fields().indexFromName('Descript_2'))
        #QgsVectorFileWriter.writeAsVectorFormat(self.Layer,shpfile,None,None,"ESRI Shapefile")
        print(kwargs)
        QgsVectorFileWriter.writeAsVectorFormat(self.Layer,shpfile,"utf-8",self.Layer.crs(),"ESRI Shapefile",**kwargs) 
        print('create')

    def exportLdb(self,lfile=None,lpad=None):

        assert self.Layer.geometryType()==1,'Alleen voor lijn-lagen'

        file_name=self.getFilename(lfile,lpad,'ldb')
        Feat=self.Layer.getFeatures()
        #map=np.array(np.zeros(0,))
        map=[]
        x=0
        for Fe in Feat:
            valdict={}
            valdict=self.coor2Dict(Fe)
            #for v in self.getFields():
            #    if Fe[v[0]] != NULL:
            #        if v[1]=='QDate':
            #            val=Fe[v[0]].toString()
            #        else:
            #            val=Fe[v[0]]
            #            print val
            #        valdict[v[0]]=val
            #if x==0:
            #    map=np.array(valdict)
            #else:
            #    map=np.append(map,valdict)
            map.append(valdict)
            x=x+1
        #return map
        g=open(os.path.join(lpad,lfile),'w')
        i=1
        for m in map:
            g.write('L{:>03}\n'.format(i))
            i=i+1
            x=m['x'];y=m['y']

            r=len(x)
            c=2
            g.write('{:>3}{:>3}\n'.format(r,c))
            for j in range(r):
                g.write('{:18f}{:18f}\n'.format(x[j],y[j]))
        g.close()
    #savemat({'qgis':map},file_name)

class ImportDivers(VectorImportExport):
    def __init__(self,pad):
        padresult = checkpad(pad)
        if padresult:
            self.Pad=pad
        else:
            self.Pad=None

    def importShape(self,file):
    
        print(file.split('.'))
        [name,ext] = file.split('.')
        assert(ext=='shp','Geselecteerde file is geen shape.')
        #la_shp= iface.addVectorLayer(os.path.join(pad,file),name,'ogr')
        la_shp = QgsVectorLayer(os.path.join(self.Pad,file),name,'ogr')
        QgsProject.instance().addMapLayer(la_shp)
        return la_shp
        #la = iface.addVectorLayerQgsVectorLayer(os.path.join(pad,file),name)   
            
    def importWkttemp(self,wktfile,epsg,qgis_id,toscreen=True):
        """ xxxxxxx"""
        if isinstance(epsg,int):
            #uri='file:///'+wktfile+'.'+wkt_ext+'?type=csv&delimiter=,%7C&wktField='+wktfield+'&spatialIndex=no&subsetIndex=no&watchFile=no&crs=epsg:'+str(epsg)
            uri='file:///'+wktfile+'?type=csv&delimiter=,%7C&wktField=geom&spatialIndex=no&subsetIndex=no&watchFile=no&crs=epsg:'+str(epsg)
        elif isinstance(epsg,QgsCoordinateReferenceSystem):
            print('epsg als QgsCoordinateReferenceSystem-object. ik betwijfel, of dit wel goed gaat!!!!!!!!!!!!!!!')
            print('ik betwijfel, of dit wel goed gaat!!!!!!!!!!!!!!!')
            #uri='file:///'+wktfile+'.'+wkt_ext+'?type=csv&delimiter=,%7C&wktField=geom&spatialIndex=no&subsetIndex=no&watchFile=no&crs=epsg:3857'
            uri='file:///'+wktfile+'?type=csv&delimiter=,%7C&wktField='+wktfield+'&spatialIndex=no&subsetIndex=no&watchFile=no&crs=epsg:3857'
        Layer_wkt=QgsVectorLayer(uri,qgis_id,'delimitedtext')
        print(uri)
        print(wktfile+' geldig?'+str(Layer_wkt.isValid()))
        if toscreen==True:
            #QgsMapLayerRegistry.instance().addMapLayer(Layer_wkt)
            QgsProject.instance().addMapLayer(Layer_wkt)
        return Layer_wkt

    def importMatlabxyz(self,matfile,epsg):
        import matlab
        """ inlezen van een matfile (1-dimensionaal"""
        array={}
        mat=matlab.loadmat(matfile,self.Pad)
        print(mat.keys())
        if mat['X'].ndim==1:
            array['x']=mat['X']
            array['y']=mat['Y']
            array['z']=mat['Z']
        else:
            array['x']=mat['X'].flatten()
            array['y']=mat['Y'].flatten()
            array['z']=mat['Z'].flatten()
            print(array['x'].shape)
        tempfile=self.writeWktpoint(array)
        self.importWkttemp(tempfile,epsg,'mesh')

#class ImportFinelpolygon(VectorImportExport,ImportDivers,ExportVector):
class ImportFinelpolygon(ImportDivers,ExportVector):
    """klasse voor het importeren van Finel-mesh data"""
    #from VectorImportExport import ExportVector
    def __init__(self,pad):
        from inl_finel import Veld as inlF
        self.inlF=inlF
        self.Pad=pad
        self.Flowparam=['H','vel']
        self.Mesh=('mesh01','sepran','mesh2D')
        self.qgis_id='mesh'

    def writeWktmesh(self,mesh,meshtype):
        """  Schrijf Mesh (sepran, mesh01, mesh2D) weg als wkt-bestand 
        Wkt bestand is in te lezen in Qgis als delimited text.
        """
        tempfile=self.getFilename(None,None,wkt_ext)
        fid=open(tempfile,'w')
        fid.write('id,'+wktfield+',z\n')
        id=1
        for a in mesh[1]['tri']:#mesh[1]['tri']:
            fid.write(str(id)+',')
            fid.write('"POLYGON ((')
            """ 
            for b in range(0,3,1): #schrijf drie hoekpunten. 
                ii=a[b]
                if b<2:
                    fid.write('%f %f,'% (mesh[1]['x'][ii],mesh[1]['y'][ii]))
                elif b==2 and meshtype=='mesh01':
                    fid.write('%f %f))",%f\n'% (mesh[1]['x'][ii],mesh[1]['y'][ii],mesh[1]['z'][id-1]))
                elif b==2 and meshtype=='mesh2D':
                    fid.write('%f %f))"\n'% (mesh[1]['x'][ii],mesh[1]['y'][ii]))
                elif b==2 and meshtype=='sepran' :
                    fid.write('%f %f))"\n'% (mesh[1]['x'][ii],mesh[1]['y'][ii]))
                else:
                    raise InputError, "meshtype verkeerd? Kleine kans dat er iets mis is met b" 
            """
            for b in range(0,4,1): #schrijf drie hoekpunten. 
                if b<3:
                    ii=a[b]
                else:
                    ii=a[0]
                if b<3:
                    fid.write('%f %f,'% (mesh[1]['x'][ii],mesh[1]['y'][ii]))
                elif b==3 and meshtype=='mesh01':
                    fid.write('%f %f))",%f\n'% (mesh[1]['x'][ii],mesh[1]['y'][ii],mesh[1]['z'][id-1]))
                elif b==3 and meshtype=='mesh2D':
                    fid.write('%f %f))"\n'% (mesh[1]['x'][ii],mesh[1]['y'][ii]))
                elif b==3 and meshtype=='sepran' :
                    fid.write('%f %f))"\n'% (mesh[1]['x'][ii],mesh[1]['y'][ii]))
                else:
                    raise Exception#, "meshtype verkeerd? Kleine kans dat er iets mis is met b" 

            id=id+1
        fid.close()
        return tempfile


    def makeFieldmesh(self,paramnaam,nr=0):
        """ initieer een veld voor finel- attribuut"""
        from qgis.core import QgsField
        from PyQt4.QtCore import QVariant
        print(paramnaam)
        for p in paramnaam:
            if nr>0:
                Field=str(nr)+'_'+p
            else:
                Field=p
            print('makefield '+Field)
            at_field=QgsField(Field,QVariant.Double)
            self.Mesh.dataProvider().addAttributes([at_field])
        self.Mesh.updateFields()
        return Field

    def setFieldmesh(self,Dictio,nr=0 ):
        """ zet waarde  voor een attributen veld voor finel- attribuut"""
        #import processing
        x=0;y=0
        for f in processing.features(self.Mesh):
            for k in Dictio:
                if nr>0:
                    fielddescr=str(nr)+'_'+k
                else:
                    fielddescr=k
                new_field_index = self.Mesh.fieldNameIndex(fielddescr)
                finelval=Dictio[k]
                if Dictio[k].mask[x]==False:
                    self.Mesh.changeAttributeValue(f.id(),new_field_index,float(Dictio[k][x])) 
                else:
                    self.Mesh.changeAttributeValue(f.id(),new_field_index,None) 
            x=x+1;y=y+1
            if y==10000:
                print('rij: '+str(x+1))
                print(new_field_index)
                print(float(Dictio[k][x]))
                y=0

    def setFieldmesh2(self, Dictio,nr=0):
        """ zet waarde  voor een attributen veld voor finel- attribuut, sneller dan 1"""
        #import processing
        provider = self.Mesh.dataProvider()
        
        for k in Dictio:
            updateMap={}
            finelval=Dictio[k]
            x=0;y=0
            for f in processing.features(self.Mesh):
                if nr>0:
                    fielddescr=str(nr)+'_'+k
                else:
                    fielddescr=k
                new_field_index = self.Mesh.fieldNameIndex(fielddescr)
                if len(Dictio[k].mask.shape)==0:
                    updateMap[f.id()] = {new_field_index: float(finelval[x])}
                elif Dictio[k].mask[x]==False:
                    updateMap[f.id()] = {new_field_index: float(finelval[x])}
                else:
                    updateMap[f.id()] = {new_field_index: None}
                x=x+1;y=y+1
                if y==20000:
                    print('rij: '+str(x+1))
                    y=0
            provider.changeAttributeValues(updateMap)

    def importMesh(self,epsg,meshfile,imp_exp,meshtype='sepran'):
        """importeren van een mesh bestand naar:
        1) tmp.dat bestand met wkt-bestandsformaat!
        2) VectorLayer-object
        """
        assert(self.Mesh.count(meshtype)>0),'Meshtype onbekend.'+ 'kies een van volgende '+self.Mesh
        #inlezen van mesh-grid
        mesh=self.inlF().mesh(self.Pad,meshtype,meshfile=meshfile,impexp=imp_exp)
        #preprocess1: verwijder tmplaag uit QGIS-registry.
        #self.removeTemplayer()

        #preprocess2:schrijven van tmp-wkt bestand in WKT-formaat
        tempfile=self.writeWktmesh(mesh,meshtype)

        #Importeren wkt-bestand van een VectorLayerObject
        Layer_wkt=self.importWkttemp(tempfile,epsg,'mesh',toscreen=False)

        #Wegschrijven naar (tijdelijke) shape-file
        crs_wkt=Layer_wkt.crs()
        QgsVectorFileWriter.writeAsVectorFormat(Layer_wkt,tempfile,None,crs_wkt) 
        Layer_shp=QgsVectorLayer(tempfile+'.shp',self.qgis_id,'ogr')
        Layer_shp.setCrs(crs_wkt)
        #QgsMapLayerRegistry.instance().addMapLayer(Layer_shp)
        QgsProject.instance().addMapLayer(Layer_shp)
        self.Mesh=Layer_shp
        print(Layer_shp.crs().description())
        return Layer_shp


    def appendFlow(self,nr,**kwargs):
        """ Voeg Flow mat bestand toe aan mesh-laag 
        nr= nummer flow-matfile (integer)
        **kwargs: 
                meshlayer: naam
                param: Specifieke parameter (string, voor mogelijke waarden zie...... )

        Op twee manieren kun je de mesh opgeven:
        OPTIE 1) Mesh wordt als QgsVectorLayer opgegeven. Geef voor variabele meshlayer een laag op.
                Bijvoorbeeld ml=iface.activeLayer()
                VectorImportExport.ImportMesh(directory).appendFlow(1,meshlayer=ml)
        OPTIE 2) Mesh is al attribuut van het object importMesh.
            Bijvoorbeeld: 
                obj=VectorImportExport.ImportMesh(directory).importMesh(epsg,meshfilenaam,'exp',meshtype='sepran')
                obj.appendFlow(1)
        """
        #OPTIE 1
        if kwargs.has_key('meshlayer'):
            meshlayer=kwargs['meshlayer']
            assert(isinstance(meshlayer,QgsVectorLayer)),"Waarschijnlijk Ongeldige laag. 1)selecteer een laag met de naam mesh"
            assert(meshlayer.name()=='mesh'),'selecteer een laag met de naam mesh'
            self.Mesh=meshlayer 
        #OPTIE 2
        else: 
            assert(hasattr(self,'Mesh')),'Mesh nog niet ingelezen, of bevat geen features: importeer eerst de mesh in!'
            meshlayer=self.Mesh

        if kwargs.has_key('param'):
            param=param
        else:
            param=self.Flowparam
        Flow=self.inlF().flow(nr,self.Pad)
        Dictio=self.preprocessImport(Flow,param)
        assert(Flow['H'].shape[0]==self.Mesh.featureCount()),('Mesh en asciifile hebben niet zelfde lengte.\n'
        'Flow[\'H\'].shape[0]='+str(Flow['H'].shape[0])+',self.Mesh.featureCount()='+str(self.Mesh.featureCount()) +'\n'
        '1) ascii voor ander mesh, 2)koppelt sepran mesh aan mat flow?')

        self.Mesh.startEditing()
        self.makeFieldmesh(Dictio,nr)
        self.setFieldmesh2(Dictio,nr)
        self.Mesh.commitChanges()
        print('FlowXX'+str(nr) +'toegevoegd aan ' +self.Mesh.source())

    def appendAscii(self,asciifile,imp_exp,meshlayer=None,*args):
        """ Voeg Ascii  bestand toe aan mesh-laag.
        asciifile = filenaam (string)
        imp_exp = impliciet of expliciet model ('imp' /'exp')
        meshlayer = naam laag mesh in legenda(string)
        *args  =....??
        """
        
        print(meshlayer)
        Dictio={}
        if meshlayer==None:# Optie 1) 
            assert(hasattr(self,'Mesh')),'Mesh nog niet ingelezen, of bevat geen features: geef eerst de mesh op!'
        elif (meshlayer,QgsVectorLayer): # Optie 2) 
            assert(meshlayer.name()=='mesh'), "Ongeldige laag. 1)selecteer een laag met de naam mesh "+meshlayer.name()
            self.Mesh=meshlayer
        else:
            raise Exception#, 'Geen meshlaag opgegeven'
        z=self.inlF().ascii(asciifile,self.Pad)
        if imp_exp=='exp':
            print('z')
            print(z)
            #Dictio[asciifile[-3:]]=z
            Data={asciifile[-3:]:z}
            print(Data)
            Dictio=self.preprocessImport(Data,[asciifile[-3:]])
        elif imp_exp=='imp':
            z2=np.zeros(self.Mesh.featureCount())
            if len(args)>0:
                mesh=args[0]
                a=0
                for tri in mesh['tri']:
                    z2[a]=z[tri].mean()
                    a=a+1
                Data={asciifile[-3:]:z2}
                Dictio=self.preprocessImport(Data,[asciifile[-3:]])
            else:
                raise TypeError#, 'voeg nog mesh toe (inlfinel)'

        if Dictio[asciifile[-3:]].shape[0]!=self.Mesh.featureCount():
            print(Dictio[asciifile[-3:]].shape[0])
            print(self.Mesh.featureCount())
            raise Exception#, 'Mesh en asciifile hebben niet zelfde lengte. 1) ascii voor ander mesh, 2)Wordt  mesh01 aan sepran-ascii gekoppeld?'
        self.Mesh.startEditing()
        self.makeFieldmesh(Dictio)
        self.setFieldmesh2(Dictio)
        self.Mesh.commitChanges()
        print(asciifile +' toegevoegd aan ' +self.Mesh.source())

#class ImportFinelpoint(VectorImportExport,ImportDivers):
class ImportFinelpoint(ImportDivers):
    """Klasse voor het importeren van een finel VELD, als PUNTEN qgislaag.
    """
    def __init__(self,pad):
        from inl_finel import Veld as inlF
        self.Pad=pad
        self.inlF=inlF
        self.Flowparam=['H','U','V']
        self.ext='.mat'

    def importFlow(self,epsg,nr,mesh,param=None,flowpad=None):
        """ importeren Flow-bestand: 
        epsg= coordinatensysteem via epsg-code (integer|QgsCoordinateReferenceSystem)
        nr = nummer flow-file (integer)
        mesh= mesh ingelezen met inl_finel (numpy array)
        param= parameter naam,   (string of list)"""
        #import vector
        if flowpad==None:
            flowpad=self.Pad
        Flow=self.inlF().flow(nr,flowpad)
        Dictio=self.preprocessImport(Flow,param)
        Dictio['x']=mesh['xe'];
        Dictio['y']=mesh['ye'];
        if Flow['H'].shape[0]!=Dictio['x'].shape[0]:
            raise Exception#, 'Mesh en asciifile hebben niet zelfde lengte. 1) ascii voor ander mesh, 2)koppelt sepran mesh aan FLow.mat?'
        tempfile=self.writeWktpoint(Dictio)
        self.importWkttemp(tempfile,epsg,str(nr))

    def importAscii(self,epsg,veldfile,mesh,imp_exp,param=None):
        """ """
        assert(imp_exp=='exp' or imp_exp=='imp'),'geef imp of exp op, opgegeven is:' +imp_exp
        if param==[]:
            param=veldfile[-3:]
        z=self.inlF().ascii(veldfile,self.Pad)
        Dictio={}
        Dictio[param]=z

        if imp_exp=='exp':
            Dictio['x']=mesh[1]['xe'];
            Dictio['y']=mesh[1]['ye'];
        else: #imp_exp=='imp':
            Dictio['x']=mesh[1]['x'];
            Dictio['y']=mesh[1]['y'];
        assert(z.shape[0]!=Dictio['x']), 'Mesh en asciifile hebben niet zelfde lengte.\n 1) ascii voor ander mesh,\n 2)koppelt sepran ascii-veld aan mesh01.mat?'

        tempfile=self.writeWktpoint(Dictio)
        self.importWkttemp(tempfile,epsg,param)

#class ImportWaqua(VectorImportExport,ImportDivers):
class ImportWaqua(ImportDivers):
    def __init__(self):
        from inl_waqua import veld as inlW
        import waquagrid_toolkit as wgtk 
        self.wgtk=wgtk
        self.inlW=inlW

    def returninltype(self,xfile,xypad):
        ext=os.path.splitext(xfile)
        print(ext)
        if ext[1]=='.mat':
            inltype='getdatamat'
        elif ext[1]=='':
            if os.path.exists(os.path.join(xypad,xfile+'.mat')):
                inltype='getdatamat'
        else:
            inltype='box'
        return inltype

    def returnXYobject(self,*arg):
        """
        Omzetten van diverse invoer naar 
        x en y-objecten  in de vorm van  
        wgtk-Depveld -object OF wgtk-Sepveld-object
        
        input: 
            divers: zie hieronder
        output:
            XObject, Yobject
        """
        xfile=None;yfile=None;rgfpad=None;
        
        #verwijder argumenten met None!
        arg=list(arg)
        for a in range(arg.count(None)):
            arg.remove(None)
        print(arg)
        if len(arg)==1:
            #MODUS 1
            #ARG[0]=pad+file rgf (str)
            if type(arg[0])==str: 
                splitdirfile=arg[0].rsplit('\\',1)
                print(len(splitdirfile))
                if len(splitdirfile)==1:
                    splitdirfile=arg[0].rsplit('/',1)
                    if len(splitdirfile)==1:
                        raise TypeError#,"string is geen geldige pad naar een rgffile:" +arg[0]
                rgfdir=splitdirfile[0]
                rgffile=splitdirfile[1]
                rgf=self.wgtk.Rgfveld(rgffile,rgfdir)
                Xobject=self.wgtk.Depveld(rgf.Xdep.Veld)
                Yobject=self.wgtk.Depveld(rgf.Ydep.Veld)
                #return Xobject,Yobject
            #MODUS 2
            #ARG[0]=wgtk.Rgfveld (object)
            if isinstance(self.wgtk.Rgfveld,arg[0]):
                Xobject=arg[0].Rgfveld.Xdep
                Yobject=arg[0].Rgfveld.Ydep
                #return Xobject,Yobject
            else:
                raise TypeError#, "Input moet bestaan uit dictionary of padfile naar rgf"  

        if len(arg)==2:
            #MODUS 3
            #ARG[0] = rgffilenaam: str
            #ARG[1] = xydir:       str
            if type(arg[0])==str: 
                rgffile=arg[0]
                if type(arg[1])==str:
                    rgfdir=arg[1]
                    rgf=self.wgtk.Rgfveld(rgffile,rgfdir)
                else:
                    raise TypeError#, "inputparameters zijn van verschillend type,"+str(type(arg[0]))+ str(type(arg[1]))
                Xobject=self.wgtk.Depveld(rgf.Xdep.Veld)
                Yobject=self.wgtk.Depveld(rgf.Ydep.Veld)
                #return Xobject,Yobject
            #MODUS 4
            #ARG[0] = X,  object wgtk.Depveld/wgtk.Sepveld 
            #ARG[1] = Y, object wgtk.Depveld/wgtk.Sepveld 
            elif isinstance(arg[0],self.wgtk.Depveld) or isinstance(arg[0],self.wgtk.Sepveld): 
                Xobject=arg[0]
                Yobject=arg[1]
            else:
                raise TypeError#, str(type(arg[0]))+ str(type(arg[1]))
        if len(arg)==3:
            assert(arg[2]!='dep' or arg[2]!='sep'), "3e invoerparameter moet dep of sep zijn, check invoer"
            #MODUS 5
            #MODUS 5
            #ARG[0] = x-array, np.ndarray
            #ARG[1] = y-array np.ndarray
            #ARG[2] = 'dep/sep'
            print(type(arg[0]))
            if isinstance(arg[0],np.ndarray) and isinstance(arg[1],np.ndarray): 
                Xveld=arg[0]
                Yveld=arg[1]
                if arg[2]=='sep':
                    Xobject=self.wgtk.Sepveld(Xveld)
                    Yobject=self.wgtk.Sepveld(Yveld)
                else:
                    Xobject=self.wgtk.Depveld(Xveld)
                    Yobject=self.wgtk.depveld(Yveld)
                #return Xobject,Yobject
            #MODUS 6
            #ARG[0] = filenaam,str
            #ARG[1] = pad str
            #ARG[2] = 'dep/sep'
            elif type(arg[0])==str and type(arg[1])==str and arg[2]=='sep':
                rgf=self.wgtk.Rgfveld(arg[0],arg[1])
                xzeta,yzeta=rgf.return_dep2wat()
                Xobject=self.wgtk.Sepveld(xzeta)
                Yobject=self.wgtk.Sepveld(yzeta)
                
            else:
                raise TypeError#, "inputparameters zijn geen numpy arrays type"
        if len(arg)==4:
            #MODUS 7
            #arg[0] = xfilenaam, str. Filetype getdatamat of box: 
            #arg[1] = yfilenaam: str. Filetype getdatamat of box: 
            #arg[2] = xydir: str
            #arg[3] = 'sep'/'dep'
            sepofdep=None
            g=0;
            for a in arg:
                if type(a)!=str:
                    raise TypeError#,"bij 4 invoerparameters mag alleen strings opgeven"
            print(arg[2].find('/')>-1)
            if arg[2].find('/')==-1 or arg[2].find('\\')==-1:
                xypad=arg[2]
            else:
                raise TypeError#,"eerste parameter bevat pad naar x en y files:" +arg[0]
                
            assert os.path.exists(xypad),"Opgegeven pad is incorrect: " +xypad
            xfile=arg[0]
            yfile=arg[1]
            xydir=arg[2]
            print('inputparameter '+ xfile+ '= x-file')
            print('inputparameter '+ yfile+ '= y-file')
            assert(arg[3]!='dep' or arg[3]!='sep'), "4e invoerparameter moet dep of sep zijn, check invoer"
            inltype=self.returninltype(xfile,xydir)
            if arg[3]=='sep':
                Xobject=self.wgtk.Sepveld(xfile,xypad,inltype)
                Yobject=self.wgtk.Sepveld(yfile,xypad,inltype)
            else:#elif arg[3]=='dep':
                Xobject=self.wgtk.Depveld(xfile,xypad,inltype)
                Yobject=self.wgtk.Depveld(yfile,xypad,inltype)
        return Xobject,Yobject


#class ImportWaquapolygon(VectorImportExport,ImportWaqua,ImportDivers):
class ImportWaquapolygon(ImportWaqua,ImportDivers):
    def __init__(self):
        from inl_waqua import veld as inlW
        self.inlW=inlW
        import waquagrid_toolkit as wgtk 
        self.wgtk=wgtk
        self.hoekpunten=[[0,0],[1,0],[1,1],[0,1]]

    def writeWktrgf(self,xzeta,yzeta,Z=None):
        #if Z!=None:
        #    assert yzeta.shape==Z.shape
        tempfile=self.getFilename(None,None,wkt_ext)
        fid=open(tempfile,'w')
        fid.write('id,'+wktfield+',m,n\n')
        m=int();n=int()
        id=1
        for i in range(xzeta.shape[0]):
            for j in range(xzeta.shape[1]):
                try:
                    if np.ma.is_masked(xzeta[i:i+2,j:j+2])==False:
                        m=i+1;n=j+1
                        fid.write(str(id)+',')
                        fid.write('"POLYGON ((')

                        for hoekp in self.hoekpunten: #schrijf vier hoekpunten. 
                            dm=hoekp[0]
                            dn=hoekp[1]
                            x=xzeta[i+dm,j+dn]
                            y=yzeta[i+dm,j+dn]
                            fid.write('%f %f ,'% (x,y))
                        if Z!=None:
                            z=Z[i+dm,j+dn]
                            fid.write('))",%d,%d,%f \n'% (m,n,z))
                        else:
                            fid.write('))",%d,%d \n'% (m,n))
                        id=id+1
                except:
                    print(i,j)
        fid.close()
        return tempfile
        
    def importRgf(self,epsg,rgffile,pad,toscreen=True):
        xzeta,yzeta=self.returnXYobject(rgffile,pad,'sep')
        #rgf=self.inlW().rgf(rgffile,pad)
        #xzeta,yzeta=self.wgtk.Rgfveld(rgf[0],rgf[1]).return_dep2wat()
        #return xzeta,yzeta
        if toscreen==True:
            # verwijder tmplaag uit QGIS-registry.
            self.removeTemplayer()
            #schrijven van tmp.dat bestand in WKT-formaat
            tempfile=self.writeWktrgf(xzeta.Veld,yzeta.Veld)
            self.importWkttemp(tempfile,epsg,'rgf')
        else:
            mc,nc=xzeta.return_mncompressed()
            #raise NotImplementedError
            #rgfdict.update{'x':xzeta,'y':xzeta,}
            #Dictio=self.preprocessImport(rgf,['x','y','m','n'])
            rgfmask=xzeta.Veld.mask
            Dictio={'x':xzeta.return_veldcompressed(),'y':yzeta.return_veldcompressed(),'m':mc,'n':nc}
            return Dictio,rgfmask
    
    def importBox(self,epsg,bfile,bpad,rgffile,rgfpad):
        print(dir(self.inlW))
        xzeta,yzeta=self.returnXYobject(rgffile,rgfpad,'sep')
        Z=self.inlW().box(bfile,bpad)
        #print xzeta.Veld.shape
        #print Z.shape
        #return
        self.removeTemplayer()
        #schrijven van tmp.dat bestand in WKT-formaat
        tempfile=self.writeWktrgf(xzeta.Veld,yzeta.Veld,Z)
        self.importWkttemp(tempfile,epsg,'box')

#class ImportWaquapoint(VectorImportExport,ImportWaqua,ImportDivers):
class ImportWaquapoint(ImportWaqua,ImportDivers):
    def __init__(self):
        import inl_waqua as inlW
        self.inlW=inlW
        import waquagrid_toolkit as wgtk
        self.wgtk=wgtk

    def importRgf(self,epsg,rgffile,pad,toscreen=False):
        """importeren van een rgf bestand naar:
        1) tmp.dat bestand met wkt-bestandsformaat!
        2) VectorLayer-object
        """
        #inlezen van mesh-grid
        rgf1=self.wgtk.Rgfveld(rgffile,pad)
        """
        #mveld,nveld=rgf1.Xdep.return_mnveld()
        #m2=mveld.flatten()
        #n2=nveld.flatten()
        #x2=rgf1.Xdep.Veld.flatten()
        #y2=rgf1.Ydep.Veld.flatten()
        #rgf1=self.inlW.veld().rgf(rgffile,pad)
        #m= np.ma.array([range(1,rgf1[0].shape[0]+1),]*rgf1[0].shape[1],mask=rgf1[0].mask.T,dtype='i').T
        #n= np.ma.array([range(1,rgf1[0].shape[1]+1),]*rgf1[0].shape[0],mask=rgf1[0].mask,dtype='i')
        """
        mcompr,ncompr=rgf1.Xdep.return_mncompressed()
        xcompr=rgf1.Xdep.return_veldcompressed()
        ycompr=rgf1.Ydep.return_veldcompressed()
        rgfmask=rgf1.Xdep.Veld.mask
        """
        #Mmax=rgf1.roostereigenschappen.Mmax
        #Nmax=rgf1.roostereigenschappen.Nmax
        #m= np.ma.array([range(1,Mmax+1),]*Nmax,mask=rgfmask.T,dtype='i').T
        #n= np.ma.array([range(1,Nmax+1),]*Mmax,mask=rgfmask,dtype='i')
        #m2=np.ma.compressed(m)
        #n2=np.ma.compressed(n)
        #x2=np.ma.compressed(rgf1[0])
        #y2=np.ma.compressed(rgf1[1])
        #x2=np.ma.compressed(rgf1.Xdep.Veld)
        #y2=np.ma.compressed(rgf1.Ydep.Veld)
        #rgf2={'x':x2,'y':y2,'m':m2,'n':n2}  
        """
        rgf2={'x':xcompr,'y':ycompr,'m':mcompr,'n':ncompr}  
        Dictio=self.preprocessImport(rgf2,['x','y','m','n'])
        if toscreen==True:
            # verwijder tmplaag uit QGIS-registry.
            self.removeTemplayer()
            #schrijven van tmp.dat bestand in WKT-formaat
            tempfile=self.writeWktpoint(Dictio)
            self.importWkttemp(tempfile,epsg,'rgf')
        else:
            #rgfmask=rgf1[0].mask
            return Dictio,rgfmask
        #return rgf2

    def importBox(self,epsg,bfile,bpad,rgffile,rpad):
        """ importeren van een box file, bijvoorbeeld voor bodemfiles
        """
        rgf1=self.wgtk.Rgfveld(rgffile,rpad)
        rgfmask=rgf1.Xdep.Veld.mask
        Z=self.inlW.veld().box(bfile,bpad)
        Zm=np.ma.array(Z,mask=rgfmask[0:Z.shape[0],0:Z.shape[1]])
        Z2=np.ma.compressed(Zm)

        Dictio,rgfmask=self.importRgf(epsg, rgffile,rpad)

        Dictio.update({'z':Z2})
        print(Dictio['x'].shape)
        print(Dictio['y'].shape)
        print(Dictio['z'].shape)
        
        self.removeTemplayer()
        #schrijven van tmp.dat bestand in WKT-formaat
        tempfile=self.writeWktpoint(Dictio)
        self.importWkttemp(tempfile,epsg,'box')
        return Z

    def importBoxdep(self,epsg,bfile,bpad,rgforxdep,ydep=None,xydir=None):
        inltype=self.returninltype(bfile,bpad)
        assert (inltype=='box'),'Alleen geschikt voor box-files'

        #Z=self.inlW.veld().box(bfile,bpad)
        Z=self.wgtk.Depveld(bfile,bpad,'box')
        Zm=np.ma.array(Z.Veld,mask=rgfmask[0:Z.Veld.shape[0],0:Z.Veld.shape[1]])
        Zc=np.ma.compressed(Zm)
        
        """
        if xydir==None :
            if ydep==None:
                Xobj,Yobj=self.returnXYobject(rgforxdep)
            else:
                Xobj=self.returnXYobject(os.path.join(rgforxdep))
                Yobj=self.returnXYobject(os.path.join(ydep))
        else:
            Xobj,Yobj=self.returnXYobject(rgf,rpad)
        """
        Xobj,Yobj=self.returnXYobject(rgforxdep,ydep,xydir)
        rgfmask=Xobj.Veld.mask
        mc,nc=Xobj.return_mncompressed()
        xc=Xobj.return_veldcompressed()
        yc=Yobj.return_veldcompressed()

        Dictio={'x':xc,'y':yc,'m':mc,'n':nc,'z':Zc}
        self.removeTemplayer()
        #schrijven van tmp.dat bestand in WKT-formaat
        tempfile=self.writeWktpoint(Dictio)
        self.importWkttemp(tempfile,epsg,'box')

    def importMat(self,epsg,mfile,mpad,x,y,xydir=None,sepdep='sep'):
        inltype=self.returninltype(mfile,mpad)
        assert (inltype=='getdatamat'),'Alleen geschikt voor getdatamat-files'
        if sepdep=='sep':
            Z=self.wgtk.Sepveld(mfile,mpad,'getdatamat')
        else:
            Z=self.wgtk.Depveld(mfile,mpad,'getdatamat')
        Xobj,Yobj=self.returnXYobject(x,y,xydir,sepdep)
        """
        if xydir==None:
            if sepdep=='sep':
                Xobj=self.wgtk.Sepveld(x)
                Yobj=self.wgtk.Sepveld(y)
            elif sepdep=='dep':
                Xobj=self.wgtk.Depveld(x)
                Yobj=self.wgtk.Depveld(y)
        elif xydir==None:
            if sepdep=='sep':
                Xobj=self.wgtk.Sepveld(x,xydir)
                Yobj=self.wgtk.Sepveld(y,xydir)
            elif sepdep=='dep':
                Xobj=self.wgtk.Depveld(x,xydir)
                Yobj=self.wgtk.Depveld(y,xydir)
        """
        rgfmask=Xobj.Veld.mask
        zmask=Z.Veld.mask

        #try:
        #Z2=Z.set_maskveld(Z.Veld,rgfmask)
        #except:
        #return Z,rgfmask
        
        Xm=np.ma.array(Xobj.Veld,mask=zmask[0:Xobj.Veld.shape[0],0:Xobj.Veld.shape[1]])
        #Xc=np.ma.compressed(Xm)
        Ym=np.ma.array(Yobj.Veld,mask=zmask[0:Yobj.Veld.shape[0],0:Yobj.Veld.shape[1]])
        #Yc=np.ma.compressed(Ym)
        if sepdep=='sep':
            Xobj2=self.wgtk.Sepveld(Xm)
            Yobj2=self.wgtk.Sepveld(Ym)
        elif sepdep=='dep':
            Xobj2=self.wgtk.Depveld(Xm)
            Yobj2=self.wgtk.Depveld(Ym)
        #return Xobj2
        mc,nc=Xobj2.return_mncompressed()

        Zm=np.ma.array(Z.Veld,mask=rgfmask[0:Z.Veld.shape[0],0:Z.Veld.shape[1]])
        Zc=np.ma.compressed(Zm)
        #mc,nc=Xobj.return_mncompressed()
        #xc=Xobj.return_veldcompressed()
        #yc=Yobj.return_veldcompressed()
        xc=Xobj2.return_veldcompressed()
        yc=Yobj2.return_veldcompressed()
        Dictio={'x':xc,'y':yc,'m':mc,'n':nc,'z':Zc}
        self.removeTemplayer()
        #schrijven van tmp.dat bestand in WKT-formaat
        #return Dictio
        tempfile=self.writeWktpoint(Dictio)
        self.importWkttemp(tempfile,epsg,'mat')

    def importPoint(self,epsg,pfile,ppad,xzeta,yzeta,xydir=None):
        Punt=self.wgtk.Punt(pfile,ppad)
        if xydir ==None:
            xzeta,yzeta=self.returnXYobject(xzeta,yzeta,'sep')
        else:
            xzeta,yzeta=self.returnXYobject(xzeta,yzeta,xydir,'sep')
        """
        if xydir==None:
            if isinstance(xzeta,self.wgtk.Sepveld):
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta)
            elif type(xzeta)==np.ndarray:
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta,'sep')
            else:
                raise TypeError
        else:
            if type(xzeta)==str:
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta,xydir,'sep')
            else:
                raise TypeError
        """
        Punt.add_xy(xzeta.Veld,yzeta.Veld)
        nr,name,m,n,x,y=Punt.return_puntlist()
        Data={'nr':nr,'name':name,'x':x,'y':y,'m':m,'n':n}
        Dictio=self.preprocessImport(Data,['nr','name','x','y','m','n'])
        tempfile=self.writeWktpoint(Dictio)
        self.importWkttemp(tempfile,epsg,'Point')

    def importDam(self,epsg,damfile,dampad,xzeta,yzeta,xydir=None):
        Dam=self.wgtk.Dam(damfile,dampad)
        if xydir ==None:
            xzeta,yzeta=self.returnXYobject(xzeta,yzeta,'sep')
        else:
            xzeta,yzeta=self.returnXYobject(xzeta,yzeta,xydir,'sep')
        """
        if xydir==None:
            if isinstance(xzeta,self.wgtk.Sepveld):
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta)
            elif type(xzeta)==np.ndarray:
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta,'sep')
            else:
                raise TypeError
        else:
            if type(xzeta)==str:
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta,xydir,'sep')
            else:
                raise TypeError
        """
        xydam=Dam.return_xy(xzeta.Veld,yzeta.Veld)
        Data={'x':xydam[:,0],'y':xydam[:,1]}
        #Dictio=self.preprocessImport(Data)
        Dictio=Data
        tempfile=self.writeWktpoint(Dictio)
        self.importWkttemp(tempfile,epsg,'dam')
        #return Dictio

#class ImportWaqualine(VectorImportExport,ImportWaqua,ImportDivers):
class ImportWaqualine(ImportWaqua,ImportDivers):
    def __init__(self):
        import inl_waqua as inlW
        import waquagrid_toolkit as wgtk 
        self.wgtk=wgtk
        self.inlW=inlW

    def writeWktline(self,xylijn,attributes=None):
        tempfile=self.getFilename(None,None,wkt_ext)
        fid=open(tempfile,'w')
        
        wktfield='geom'
        
        fid.write('id,'+wktfield+',')
        if attributes!=None:
            for attr in attributes:
                fid.write(attr+',')
        fid.write('\n')

        id=1
        m=0
        for line in xylijn:
            fid.write(str(id)+',')
            fid.write('"LINESTRING (')
            for a in range(line.shape[0]):
                x=line[a,0];y=line[a,1]
                fid.write('%f %f,'% (x,y))
            fid.write(')",')
            if attributes!=None:
                for attr in attributes:
                    val= attributes[attr][m]
                    fid.write('%f,'% val)
                m=m+1
            fid.write('\n')
            id=id+1
        fid.close()
        return tempfile

    def importEncl(self,epsg,enclfile,enclpad,xzeta,yzeta,xydir=None):
        Encl=self.wgtk.Enclosure(enclfile,enclpad)
        
        if xydir ==None:
            xzeta,yzeta=self.returnXYobject(xzeta,yzeta,'sep')
        else:
            xzeta,yzeta=self.returnXYobject(xzeta,yzeta,xydir,'sep')
        """
        if xydir==None:
            if isinstance(xzeta,self.wgtk.Sepveld):
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta)
            elif type(xzeta)==np.ndarray:
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta,'sep')
            else:
                raise TypeError
        else:
            if type(xzeta)==str:
                xzeta,yzeta=self.returnXYobject(xzeta,yzeta,xydir,'sep')
            else:
                raise TypeError
        """
        xyencl=Encl.return_xycoor(xzeta,yzeta)
        tempfile=self.writeWktline(xyencl)
        self.importWkttemp(tempfile,epsg,'encl')
        return xyencl

    def importSchot(self,epsg,schotfile,schotpad,rgforxdep,ydep=None,xydir=None):
        Schot=self.wgtk.Schotje(schotfile,schotpad)
        xdep,ydep=self.returnXYobject(rgforxdep,ydep,xydir)
        """
        if xydir==None:
            if ydep==None:
                xdep,ydep=self.returnXYobject(rgforxdep)
            if isinstance(rgforxdep,self.wgtk.Depveld):
                xdep,ydep=self.returnXYobject(rgforxdep,ydep)
            elif type(rgforxdep)==np.ndarray:
                xdep,ydep=self.returnXYobject(rgforxdep,ydep,'dep')
            else:
                raise TypeError
        else:
            if type(rgforxdep)==str:
                xdep,ydep=self.returnXYobject(rgforxdep,xydir)
            else:
                raise TypeError
        """
        xyschot=Schot.return_xy(xdep.Veld,ydep.Veld)
        tempfile=self.writeWktline(xyschot)
        self.importWkttemp(tempfile,epsg,'schot')

    def importRuwheidarea(self,epsg,ruwfile,ruwpad,uvtype,rgforxdep,ydep=None,xydir=None):
        Ruwheid=self.wgtk.Ruwheidarea(ruwfile,ruwpad,uvtype)
        xdep,ydep=self.returnXYobject(rgforxdep,ydep,xydir)

        """
        if xydir==None:
            if ydep==None:
                xdep,ydep=self.returnXYobject(rgforxdep)
            if isinstance(rgforxdep,self.wgtk.Depveld):
                xdep,ydep=self.returnXYobject(rgforxdep,ydep)
            elif type(rgforxdep)==np.ndarray:
                xdep,ydep=self.returnXYobject(rgforxdep,ydep,'dep')
            else:
                raise TypeError
        else:
            if type(rgforxdep)==str:
                xdep,ydep=self.returnXYobject(rgforxdep,xydir)
            else:
                raise TypeError
        """
        xyruw=Ruwheid.return_xy(xdep.Veld,ydep.Veld)
        roughcode=[v['roughcode'] for v in Ruwheid.Lijn.values()]
        fraction=[v['fraction'] for v in Ruwheid.Lijn.values()]
        #tempfile=self.writeWktline(xyruw)
        #return xyruw
        tempfile=self.writeWktline(xyruw,{'roughcode':roughcode,'fraction':fraction})
        self.importWkttemp(tempfile,epsg,'ruw')