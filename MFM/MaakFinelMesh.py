from __future__ import division  #helpt om floating point notatie te krijgen bij delen (bijvoorbeeld voor area)

"""
Code om binnen Qgis een Finel Mesh te maken met behulp van Matlab en Triangle
Beschouw het een Google Earth plus

KORTE SAMENVATTING: 
er worden 1 (lijn) of 2 (lijn + punt) shape-files gemaakt: de zogenaamde Triangleinvoer-lagen
De shape-files worden geexporteerd  naar 1 kml bestand. 
Er wordt een m-file  gemaakt.  
De m-file en kml-bestand worden in  matlab en triangle verwerkt tot .out file. 
De out-file wordt ingelezen en in de file 

_____________________________________________________________________________
VOORBEELDEN VAN GEBRUIK MAAKFINELMESH

Voorbeeld 1): Start een blanco triangle-invoer laag.
	project= 'test'
    werkpad= 'D:/projectje'
    TriangleInvoerLijn(project,werkpad).startTriangleinvoer()
    ** Resultaat: Er wordt een nieuwe laag gemaakt met de naam trinp_lijn

Voorbeeld 2): Zet een kml bestand om in een Triangleinvoerlaag.  
    * project= 'test'
    * werkpad= 'D:/projectje'
    laad een kml file in.
    selecteer de laag in de legenda
    * TriangleInvoerLijn(project,werkpad).makeTriangleinvoer(iface.activeLayer())
    ** Resultaat:  Laag is klaar om te bewerken, of om te zetten naar een grid (Zie Volgende voorbeelden)

Voorbeeld 3): Maak een mesh (expliciet) uit een punten en lijnen Triangleinvoerlaag
Beperk de maximale celgrootte tot oppervlak 1E6. Gebruik matlab-scripts uit SvaTriangle
Plot het mesh naar het scherm.   
    De Triangleinvoerlagen hebben in de legenda namen 'trinp_lijn' en 'trinp_punt';  
    * project= 'test'
    * werkpad= 'D:/projectje'
    * Mesh(project,werkpad,'trinp_lijn','trinp_punt').integraalMesh('exp','Triangle',False,1000*1000)
    **Resultaat: File D:/projectje/test.out  Als tussenproduct wordt de m-file D:/projectje/maak_finelmodel.m 
    .out wordt omgezet naar C:/(of D:)/TEMP/tmpXXX.dat.shp en ingelezen in Qgis  .

Voorbeeld 4) Maak een mesh (impliciet) uit een Triangleinvoerlaag. 
Selecteer eerst de Triangle invoerlaag in de legenda. 
    * project= 'test'
    * werkpad= 'D:/projectje'
    Selecteer in de legenda de Triangleinvoerlaag.
    * Mesh(project,werkpad,iface.activeLayer()).makeMesh('exp','Triangle_2_beta')
    **Resultaat: File D:/projectje/test.out  
    Als tussenproduct wordt de m-file D:/projectje/maaktrianglegrid.m 

Voorbeeld 5) Maak een mesh (expliciet) uit een Triangleinvoerlaag, hoek is 35 graden
    * project= 'test'
    * werkpad= 'D:/projectje'
    * Mesh(project,werkpad,'trinp_lijn').makeMesh('exp','Triangle_3_beta',min_tri_angle=35)

________________________________________________________________________________

BESCHRIJVING CLASS

TriangleinvoerPL class:     Algemeen, voor Triangle invoer laag. 
TriangleInvoerLijn class:     Lijn elementen invoer Triangle(boundary, internals, holes)
TriangleInvoerPunt class:     Punt elementen invoer Triangle (region, point)
MakeTriangleGrid class:     class voor het maken van een m-file make_triangle_grid.m
Mesh-class:                 class voor maken en plotten van een mesh


AFHANKELIJKHEDEN BUITEN PYTHON: 
- Matlab:
        template-mfile maaktrianglegrid.m
        kml2triangle_struct_qgis.m
- Triangle.exe:

BESTANDEN DIE GEMAAKT WORDEN: 
- trinp_lijn.shp
- trinp_lijn.kml
- trinp_punt.shp
- trinp_punt.kml
- $Project.kml: combinatie trinp_lijn.kml en trinp_punt.kml
- tmpXXXX.dat.shp

"""

import VectorImportExport 
#from qgis.core import QgsGeometry,QgsCoordinateReferenceSystem,QgsField,QgsVectorLayer,QgsMapLayerRegistry
from qgis.core import QgsGeometry,QgsCoordinateReferenceSystem,QgsField,QgsVectorLayer,QgsProject
from qgis.utils import iface
from PyQt5.QtCore import QVariant
import os
import numpy as np
import re


if 'readMFMconffile' not in globals():
    readMFMconffile='C:\TEMP\default_MFM.conf'
flag_descriptionfield=['description','descriptio','Description','Descriptio']

def listFeatures(layer):
    # Get all the features in a list
    featureslist = [ feature for (feature) in layer.getFeatures()]
    #print('nr features in laag: '+str(len(featureslist)))
    return featureslist

def deleteFields(layer,fields):
    print(fields)
    assert type(fields)==list or type(fields)==tuple,"list of tuple met naam van velden om te verwijderen"

    assert isinstance(layer,QgsVectorLayer),"Laag is een vector laag"
    listind=[]
    for f in fields:
        ind=layer.fields().indexFromName(f)
        if ind>-1:
            listind.append(ind)
    layer.startEditing()
    layer.dataProvider().deleteAttributes(listind)
    layer.commitChanges()

def reverseNodes(layer):
    """Omdraaien van een lijnstuk"""
    try:
        if layer.geometryType()>0:
            layer.startEditing()
        else:
            print('Je probeert functie toe te passen op een puntlaag ! Dat Mag Niet!')
            raise Exception
    except    AttributeError:#, Argument:
        print("Omdraaien lijn niet mogelijk, geen (geldige vector-)laag geselecteerd?", Argument)

    else:
        if layer.selectedFeatures()==[]:
            featurelist= layer.getFeatures()
        else:
            featurelist= layer.selectedFeatures()
        for f in featurelist:
            print(f)
            geom = f.geometry()
            nodes = geom.asPolyline()
            if len(nodes)==0:
                nodes = geom.asMultiPolyline()
                for n in nodes:
                    n.reverse()
                assert len(nodes)>0
                newgeom = QgsGeometry.fromMultiPolylineXY(nodes)
            else:
                nodes.reverse()
                newgeom = QgsGeometry.fromPolyline(nodes)
            layer.changeGeometry(f.id(),newgeom)
        layer.commitChanges()
        print('Voor '+layer.name()+ 'geselecteerde lijn(en) omgedraaid.' )
        return nodes

def setcrsProject(crs=3857):# crs: epsg3857 ==PseudoMercator
    #setCrsTransformEnabled(), hasCrsTransformEnabled(), hasCrsTransformEnabledChanged() were removed. CRS transformation is now always enabled.
    #if iface.mapCanvas().mapRenderer().hasCrsTransformEnabled():
    my_crs=QgsCoordinateReferenceSystem(crs,QgsCoordinateReferenceSystem.EpsgCrsId)
    iface.mapCanvas().mapRenderer().setDestinationCrs(my_crs)
    print('set Project crs: '+my_crs.description())
    #else:
    #print('Niet mogelijk om crs aan te passen: hasCrsTransformEnabled')

def wgs2epsgutmzone(lon,lat):
    utmzone=np.fix((np.mean(lon) / 6 ) + 31);
    if np.mean(lat)>0:
        epsg=int(32600+utmzone)
    else:
        epsg=int(32700+utmzone)
    return epsg,utmzone

def readMFMconf(self_class,conffile,mfmclass):
    """ Inlezen van configuratiefile voor MFM
    conffile= pad en filenaam van de configuratiefile
    mfmclass= class binnen MFM waarvoor configuratieparameters ingelezen moeten worden.
    """
    print('start inlezen MFM configuratiefile: '+ conffile)
    print('Configuratie voor MFM-class: '+mfmclass)
    g=open(conffile)
    conftext=g.readlines()
    a=0;x=0
    while x==0:
        if conftext[a].find('['+mfmclass+']')!=-1:
            x=1
        a=a+1
    attribute={}
    while x==1 and a<len(conftext):
        kv= conftext[a].split('=')
        if len(kv)==2:#else=lege regel 
            print(conftext[a])
            k=kv[0]
            v=kv[1]
            #print('Variabele: '+ str(k))
            #print('Waarde: '+ str(v))
            v=v.strip() #verwijderen \n aan einde regel 
            attribute.update({k:v})
        if re.match('\s*\[\s*\w+\s*\]\s*',conftext[a])!=None:
            #print(conftext[a])
            x=2
        a=a+1
    print('einde inlezen MFM configuratiefile. ' )

    for a in attribute:
        setattr(self_class,a,attribute[a])
    return self_class

class TriangleInvoerPL:
    """ class voor het maken van een triangle invoerobject. 
    Er zijn drie manieren om een laag op te starten 
    1) startTriangleinvoer: maak blanco invoer
    2) makeTriangleinvoer: maak invoerlaag uit bestaande vectorlaag
    3) appendTriangleinvoer: haal invoerlaag uit bestaande triangleinvoerlaag
    Met de class Mesh wordt de laag omgezet naar een mesh. 
    Attributen: 
        VeldenTypes
    """
    def __init__(self,project, werkpad=os.getcwd()):
        """ class voor het maken van een triangle invoerobject. 
        Er zijn drie manieren om een laag op te starten 
        1) startTriangleinvoer: maak blanco invoer
        2) makeTriangleinvoer: maak invoerlaag uit bestaande vectorlaag
        3) appendTriangleinvoer: haal invoerlaag uit bestaande triangleinvoerlaag
        Met de class Mesh wordt de laag omgezet naar een mesh. 
        Attributen: 
            Velden
            Types
        """
        asserttekst =("\nDirectory:"+werkpad+'\nProjectnaam:'+project+'\n Directory kan niet geopend worden!\n Bestaat de Directory wel?') 
        assert(os.path.exists(werkpad)),asserttekst
        self.Pad=werkpad
        self.Layer=None
        self.Project=project #projectnaam

    def hasfieldsTriangleinvoer(self):
        """Hulpfunctie: Check of invoerlaag alle finel velden heeft"""
        for v in self.Velden:
            veldnaam =list(v.keys())[0]()
            #if laag.fields().fieldNameIndex(veldnaam)==-1:
            #print(v)
            if self.Layer.fields().fieldNameIndex(veldnaam)==-1:
                print('geen triangleinvoer laag. Ontbrekend veld: '+veldnaam)
                return False
        return True

    def hasnullTriangleinvoer(self):
        """Hulpfunctie: Check of er features zijn met verplichte waarden, die toch een waarde NULL hebben"""
        print('Start controle op NULL waarden')
        feat=listFeatures(self.Layer)
        for f in feat:
            if f.attribute('type')==None:
                print('ontbrekend type in '+ str(f.id()))
                return True

            for t in self.Typesessential:
                if f.attribute('type')==list(t.keys())[0]():
                    #for veld in t.values()[1]:
                    for veld in t['type'][1]:
                        f.attribute(veld)
                        if f.attribute(veld)==None:
                            print('bevat NULL op '+str(f.attribute('name'))+ ' '+veld  )
                            return True
                    break
        print('geen probleem met NULL waarden ')
        return False
    
    def volgordekmlTriangleinvoer(self):
        """Hulpfunctie: Bepalen volgorde waarin lijnen in kml gezet moeten worden."""
        volgorde_ori= range(self.Layer.featureCount())
        volgorde_type=[];cnum1_b=[]
        for t in self.Types:
            x=0
            for f in self.Layer.getFeatures():
                type=f.attribute('type')
                if type==list(t.keys())[0]():
                    if type.lower()=='b':
                        cnum1_b.append(f.attribute('cnum1'))
                    volgorde_type.append((x))
                x=x+1
        #instellen volgorde boundary op basis van cnum
        volgorde_cnum1=list(index for index, item in sorted(enumerate(cnum1_b), key=lambda item:item[1]))
        Volgorde= volgorde_type[len(volgorde_cnum1):]#Eerst alle niet-boundary lijnen
        volgorde_cnum1.reverse()
        for v in volgorde_cnum1:#Dan Boundary lijnen vooraan toevoegen
            Volgorde.insert(0,volgorde_type[v])
        #print(Volgorde)
        return Volgorde

    def transformgekmlTriangleinvoer(self,laag):
        """Hulpfunctie: Transformeer laag, die oorspronkelijk een google earth kml was, naar Triangleinvoer shape
        laag= is QgsVectorLayer of een shapefile  
        """
        print('Start omzetten google earth-laag naar Triangleinvoer-laag')
        if laag.isEditable()==False:
            assert(laag.startEditing()==True),'Openen voor editen niet gelukt. Mogelijke probleem: laag is geen shape, maar een kml\n'+laag.source()

        typesdict={}
        for t in self.Types: typesdict.update(t)

        for descriptionfield in  flag_descriptionfield: 
            if laag.fields().indexFromName(descriptionfield)>0:
                break
        for f in laag.getFeatures():
            #name=f.attribute('Name');print(name)
            descr=f.attribute(descriptionfield);#print(descr)
            if descr==None:
                continue
            descr=descr.strip().lower()
            type=re.search('type\s*=\s*\'\w',descr).group()[-1]
            fieldind=laag.fieldNameIndex('type')
            laag.changeAttributeValue(f.id(),fieldind, type)

            if typesdict[type][1].count('cnum1')==1:
                #print('1')
                cnumdescr=re.search('cnum\s*=\D*(\d*)\s*:*\s*(\d*)\D*',descr).groups()
                cnum1=int(cnumdescr[0])
                fieldind=laag.fieldNameIndex('cnum1')
                laag.changeAttributeValue(f.id(),fieldind, cnum1)
                if cnumdescr[1]!='':
                    fieldind=laag.fieldNameIndex('cnum2')
                    cnum2=int(cnumdescr[1])
                    laag.changeAttributeValue(f.id(),fieldind, cnum2)
            if typesdict[type][1].count('area1')==1:
                fieldind=laag.fieldNameIndex('area1')
                maxareadescr=re.search('maxarea\s*=\s*([^;\n]+)',descr).groups()[0]

                try:
                    maxareadescr=maxareadescr.replace('^','**')
                except:
                    return maxareadescr,descr
                fieldind2=laag.fieldNameIndex('area2')
                maxarea=eval(maxareadescr)
                laag.changeAttributeValue(f.id(),fieldind, maxarea)
                laag.changeAttributeValue(f.id(),fieldind2, None)

            if typesdict[type][1].count('dep')==1:
                depdescr=re.search('dep\s*=\s*(\d*)',descr)
                if depdescr!=None:
                    fieldind=laag.fieldNameIndex('dep')
                    dep=int(depdescr.groups()[0])
                    laag.changeAttributeValue(f.id(),fieldind, dep)

        laag.commitChanges()
        deleteFields(laag,['begin','end','timestamp','altitudeMo','tessellate','extrude','visibility'
        ,'drawOrder','icon'])
        print('Einde omzetten google earth-laag naar Triangleinvoer-laag')
        return laag

    def makefieldsTriangleinvoer(self):
        """Subfunctie: Aanmaken van velden in attributen tabel"""
        for v in self.Velden:
            #veldnaam =v.keys()
            veldnaam =list(v.keys())[0]
            #veldvariant =v.values()
            veldvariant =v[veldnaam][0]
            #veldlengte=v.values()[1]
            veldlengte=v[veldnaam][1]
            #if    self.Layer.fields().fieldNameIndex(veldnaam)==-1:
            if    self.Layer.fields().indexFromName(veldnaam)==-1:
                #at_field=QgsField(list(v.keys())[0](),v.values())
                at_field=QgsField(veldnaam,veldvariant)
                #at_field.setLength(v.values()[1])
                at_field.setLength(veldlengte)
                if v.values()==QVariant.Double:
                    print(v.viewkeys())
                    print(v.values()[1])
                    #at_field.setPrecision(v.values()[2])
                    at_field.setPrecision(v[veldnaam][2])
                self.Layer.dataProvider().addAttributes([at_field])
                self.Layer.updateFields()
                print('yesssssss')
            else:
                print('veld '+ veldnaam +  ' bestaat reeds')

    def returntypeinvoerTriangleinvoer(self,input,geometrytype):
        """ 
        return type invoer voor een laag en geef deze terug als QgsVectorLayer-object 
        input: object met een laag laag voorstelt. 
            geometrytype: [Point| LineString] 
        output: 2 argumenten 
            1) type laag (nr)
                1=QgsVectorLaag
                2=TriangleInvoer-class
                3=string
            2)QgsVectorLayer
        """
        import Layers
        from qgis.core import QGis

        if geometrytype=='LineString':
            qgisgeom=QGis.Line
            TI=TriangleInvoerLijn
        elif geometrytype=='Point':
            TI=TriangleInvoerPunt
            qgisgeom=QGis.Point
        else:
            raise Exception#, 'incorrecte invoer geometrytype '

        if isinstance(input,QgsVectorLayer):
            assert(input.geometryType()==qgisgeom),'input is geen '+geometrytype+ 'lijn laag'
            return 1,input
        elif isinstance(input,TI):
            assert(input.Layer.geometryType()==qgisgeom),'input is geen lijn laag'
            return 2,input.Layer
        elif type(input)==str:
            layers=Layers.returnLayersbyname(input)
            #print(layers;#print(input))
            tivlagen=[]
            for l in layers:
                #print(geometrytype)
                check=Layers.checkVectorLayerGeometryType(l,geometrytype)
                #print(check)
                if check==True:
                    tivlagen.append(l)

            if len(tivlagen)==0:
                raise AttributeError#,'laag met naam' + input +'niet aanwezig in  legenda ' 
            elif len(tivlagen)>1:
                raise Exception#,'Meerdere lijnen-lagen aanwezig in legenda met naam '+ input
            else:
                return 3,tivlagen[0]
        else:
            raise ValueError#, (input +" is Geen vectorlaag of Triangleinvoer-class instance") 

    def startTriangleinvoer(self):
        """Hoofdfunctie: start lege Triangleinvoer-laag """
        self.Layer=QgsVectorLayer(self.Layertype,self.Filaagnaam,'memory')
        assert(self.Layer.isValid()),'Laag ongeldig. Reden: onbekend'
        self.makefieldsTriangleinvoer()
        self.setLayout()
        QgsProject.instance().addMapLayer(self.Layer)
        #QgsMapLayerRegistry.instance().addMapLayer(self.Layer)
        #setcrsProject(self.Layer.crs().postgisSrid())
        self.Layer.startEditing()
        af=iface.actionAddFeature()
        af.setChecked(True)
        af.trigger()

    def makeTriangleinvoer(self,laag):
        """Hoofdfunctie: maak een  finellaag uit een bestaande vector laag
            1) Filenaam in string 
            2) QgsVectorLayer in  
            Extra optie:
                kml met model worden velden ingevuld op basis inhoud kml 
        """
        def isgoogleearth(vectorlaag):
            """is laag (ooit) gemaakt met google earth en is het een triangle invoer """
            l=vectorlaag
            try:
                if l.fields().indexFromName('Name')<0:
                    print('Geen GE-laag: bevat geen veld \'Name\'')
                    return False
                else:
                    descriptioncheck=False
                    for descr in  flag_descriptionfield: 
                        if l.fields().indexFromName(descr)>0:
                            descriptioncheck=True
                            break
                    if descriptioncheck==False:
                        print('Geen GE-laag: bevat geen veld \'Descriptio\' of \'Description\' ')
                        return False
                    else:
                        return True
            except AttributeError:
                print(l+' Geen vectorlaag')
                return False

        resulttype,laaguit=self.returntypeinvoerTriangleinvoer(laag,self.Layertype)
        if resulttype==1:
            tmplayer=laag
            laagnaam=tmplayer.name()
        elif resulttype==3:
            tmplayer=laaguit
            laagnaam=laag.rstrip('kml')
        else:
            raise TypeError#, ('opties voor \'laag\': 1)QgsVectorLayer-object#, 2) reeds ingelezen laag ')  
        print(laagnaam)

        try:
            if tmplayer.isValid()==False: 
                raise AttributeError#, 'verkeerd bestandstype?Verkeerde filenaam? Verkeerde directory?'
        except NameError:
            'Invoer moet Qgis laag zijn, of bestaande vector bestand'
        #print(tmplayer.storageType()#print(tmplayer.storageType().find('KML')))
        if tmplayer.storageType().find('KML')>-1:
            #kml files moeten weggeschreven worden naar een shape om te kunnen bewerken.
            #print(laagnaam)
            print(os.path.join(self.Pad,laagnaam+'.shp'))
            #print(tmplayer.dataProvider().fields().fieldNameIndex('Descript_2'))
            VectorImportExport.ExportVector(tmplayer).exportShp(laagnaam,self.Pad)
            tmplayer=QgsVectorLayer(os.path.join(self.Pad,laagnaam+'.shp'),laagnaam,'ogr')
            
            assert(tmplayer.isValid()==True), os.path.join(self.Pad,laagnaam)+': directory bestaat niet? problemen met schrijfrechten?'
        print(tmplayer.storageType())
        deleteFields(tmplayer,['Descript_1','descript_2'])

        self.Layer=tmplayer
        self.setLayout()
        self.makefieldsTriangleinvoer()

        if isgoogleearth(tmplayer):
            try:
                self.Layer=self.transformgekmlTriangleinvoer(self.Layer)
            except:
                print("transformeren van google earth kml naar volwaardige Triangleinvoerlaag niet helemaal")
                print("Pas de Triangle invoerlaag verder aan.")
                raise 
        QgsMapLayerRegistry.instance().addMapLayer(self.Layer)
        setcrsProject(self.Layer.crs().postgisSrid()) 
        return self.Layer

    def appendTriangleinvoer(self,vectorlaag):
        """Hoofdfunctie: Voeg een bestaande Triangleinvoer-laag toe aan een project"""
        self.Layer= vectorlaag
        print(self.Layer)
        #assert(self.hasfieldsTriangleinvoer(vectorlaag)),'geen geschikte Qgis TriangleInvoerlaag. /n Maak of selecteer eerst een triangle invoerlaag' 
        #assert(self.hasfieldsTriangleinvoer()),'geen geschikte Qgis TriangleInvoerlaag. /n Maak of selecteer eerst een triangle invoerlaag' 
        if self.hasfieldsTriangleinvoer()==False:
            print(vectorlaag +' is geen geschikte Qgis TriangleInvoerlaag. /n Maak of selecteer eerst een triangle invoerlaag')
            return False
        try:
            filaagnaam=self.Layer.name()
            print(filaagnaam)
            self.setLayout()
            setcrsProject(self.Layer.crs().postgisSrid()) 
            return True

        except Exception as msg:
            print('laag ongeschikt: geen TI laag toegevoegd')
            print(msg)
            return False
        except:
            print('overige fout in appendTriangleinvoer')
            return False

    def exportTriangleinvoer(self,fileformat='mat'):
        """Subfunctie: exporteren van qgis laag naar shp, kml en matfile"""
        pad= self.Pad
        if fileformat=='kml':
            volgorde=self.volgordekmlTriangleinvoer()
            self.makekmlTriangleinvoer()
            fl=listFeatures(self.Layer)
            laag_ori= self.Layer
            self.Layer=QgsVectorLayer(self.Layertype+'?crs=EPSG:3857',self.Filaagnaam,'memory')
            self.Layer.setCrs(laag_ori.crs())
            self.Layer.startEditing()
            self.Layer.dataProvider().addAttributes(laag_ori.fields())
            self.Layer.updateFields()
            for i in volgorde:
                self.Layer.dataProvider().addFeatures([fl[i]])
            self.Layer.commitChanges()
            #Schrijf weg naar files
            VectorImportExport.ExportVector(self.Layer).exportKml(self.Layer.name()+'.kml',pad,DescriptionField='kml',NameField='name')
        elif fileformat=='mat':
            VectorImportExport.ExportVector(self.Layer).exportMat(self.Layer.name(),pad)
        elif fileformat=='shp':
            VectorImportExport.ExportVector(self.Layer).exportShp(self.Layer.name()+'.shp',pad)
        else:
            raise AttributeError#, 'Alleen mat#, shp kml kunnen hier weggeschreven worden'
        print(os.path.join(pad,self.Layer.name())+ '.'+fileformat+' weggeschreven')


class TriangleInvoerPunt(TriangleInvoerPL):
    def __init__(self,project, werkpad=os.getcwd()):
        asserttekst =("\nDirectory:"+werkpad+'\nProjectnaam:'+project+
                    '\n Directory kan niet geopend worden!\n Bestaat de Directory wel?') 
        assert(os.path.exists(werkpad)),asserttekst
        self.Pad=werkpad
        self.Layer=None
        self.Project=project #projectnaam
        self.Layertype='Point'
        self.Velden=[{'name':(QVariant.String,20)},
                     {'type':(QVariant.String,1)}, 
                     {'area1':(QVariant.Double,20,12)},{'area2':(QVariant.Double,20,12)},
                    ]
        self.Types=[{'r':  ['region',['type','area1'],        4]},
                    {'p':  ['point',['name','type'],        5]}
                    ]
        self.Typesessential=[{'r':['region',['type','area1'],        4]},
                            {'p': ['point', ['name','type'] ,        5]}
                            ]
        self=readMFMconf(self,readMFMconffile,'TrianglePunt')

    def makekmlTriangleinvoer(self):
        """    1) Subfunctie: Voeg veld  kml toe aan attributentabel, gevuld op basis Google Earth data
            2) Bepaal volgorde (variabele Volgorde) waarin features in de tabel moeten :
                a) op basis van lijn type
                b) op basis van cnum
        """
        print('START veld kml punt')
        fieldind=self.Layer.fieldNameIndex('kml')
        self.Layer.startEditing()
        if fieldind==-1:
            print('maak Attribuutveld kml')
            self.Layer.dataProvider().addAttributes([QgsField('kml',QVariant.String)])
            self.Layer.updateFields()

        fieldind=self.Layer.fieldNameIndex('kml')
        #Attributen tabel uitbreiden met veld kml 
        for t in self.Types:
            for f in self.Layer.getFeatures():
                type=f.attribute('type')
                #print(type)
                if type==list(t.keys())[0]():
                    descrbasis= 'type=\'' + type + '\'\n'
                    if type.lower()in ['r']:
                        if f.attribute('area2')==None:
                            descr= descrbasis+ ' MaxArea='+ str(f.attribute('area1'))+'\n'
                        else:
                            descr= descrbasis+ ' MaxArea='+ str(f.attribute('area1'))+'*'+str(f.attribute('area2'))+'\n'
                    else:
                        descr='type=\'' + type + '\'\n'
                        #print(type.lower())
                    #print(descr)
                    #print(fieldind)
                    self.Layer.changeAttributeValue(f.id(),fieldind, descr)
        self.Layer.commitChanges()
        print('EINDE veld kml punt')

    def setLayout(self):
        from qgis.core import QgsMarkerSymbolV2
        try: 
            sym=QgsMarkerSymbolV2.createSimple({'name':'arrow', 'color':'red'})
            ren= self.Layer.rendererV2()
            ren.setSymbol(sym)
            ren.symbols()[0].setSize(5)
            iface.legendInterface().refreshLayerSymbology(self.Layer)
        except AttributeError:
            print('geen vectorlaag')

class TriangleInvoerLijn(TriangleInvoerPL):
    def __init__(self,project, werkpad=os.getcwd()):
        asserttekst =("\nDirectory:"+werkpad+'\nProjectnaam:'+project+
                    '\n Directory kan niet geopend worden!\n Bestaat de Directory wel?') 
        assert(os.path.exists(werkpad)),asserttekst
        self.Pad=werkpad
        self.Layer=None
        self.Project=project #projectnaam
        self.Filaagnaam='trinp_lijn'
        self.Layertype='LineString'
        self.Velden=[{'name':(QVariant.String,20)},
                    {'type':(QVariant.String,1)}, 
                    {'cnum1':(QVariant.Int,5)}, {'cnum2':(QVariant.Int,5)},
                    {'area1':(QVariant.Double,20,12)},{'area2':(QVariant.Double,20,12)},
                    {'sidelength':(QVariant.Double,10,4)},
                    {'dep':(QVariant.Double,10,4) },
                    {'remove':(QVariant.Int,1)},
                    {'dam':(QVariant.Int,1)},
                    #{'spline':(QVariant.Int,1)}
                    ]

        self.Types=[{'b':['boundary',['type','cnum1','sidelength'],"255,0,0",0]},
                    {'o':['opening',['type','cnum1','sidelength'],"255,125,0",0]},
                    {'i':['internal',['type','cnum1','dep','remove','dam','sidelength'], "0,255,0",1]},
                    {'h':    ['hole',['type','cnum1','sidelenght'],"0,0,255",2]},
                    {'a':    ['area',['type','area1'],"125,125,0",3]},
                    ]
        #attributen die een waarde moeten hebben per type
        self.Typesessential=[
                {'b':['boundary',['name','type','cnum1'],        0]},
                {'o':['opening',['name','type','cnum1'],        0]},
                {'i':['internal',['type','cnum1'],1]},
                {'h':    ['hole',['type','cnum1'],        2]},
                {'a':    ['area',['type','area1'],        3]},
                ]
        self=readMFMconf(self,readMFMconffile,'TriangleLijn')

    def makekmlTriangleinvoer(self):
        """    1) Subfunctie: Voeg veld  kml toe aan attributentabel, gevuld op basis Google Earth data
            2) Bepaal volgorde (variabele Volgorde) waarin features in de tabel moeten :
                a) op basis van lijn type
                b) op basis van cnum
        """
        fieldind=self.Layer.fieldNameIndex('kml')
        self.Layer.startEditing()
        if fieldind==-1:
            print('maak Attribuutveld kml')
            self.Layer.dataProvider().addAttributes([QgsField('kml',QVariant.String)])
            self.Layer.updateFields()

        fieldind=self.Layer.fieldNameIndex('kml')
        #Attributen tabel uitbreiden met veld kml 
        for t in self.Types:
            for f in self.Layer.getFeatures():
                type=f.attribute('type')
                if type==list(t.keys())[0]():
                    if list(t.keys())[0]()=='o':#o voor opening, wordt in kml b van boundary
                        type='b'
                    descr='type=\'' + type + '\'\n'
                    descrbasis= 'type=\'' + type + '\'\n'
                    if  t[list(t.keys())[0]()][1].count('cnum1')==1:#['b', 'h', 'i']
                        if f.attribute('cnum2')==None:
                            descr= descrbasis+ ' cnum=' +  str(f.attribute('cnum1'))+'\n' 
                        else :
                            descr= descrbasis+ ' cnum=' +  str(f.attribute('cnum1'))+':'+ str(f.attribute('cnum2'))+'\n'
                        if t[list(t.keys())[0]()][1].count('remove')==1:
                            if f.attribute('remove')!=None:
                                descr=descr+' remove='+str(f.attribute('remove'))
                        if t[list(t.keys())[0]()][1].count('dep')==1:
                            if f.attribute('dep')!=None:
                                descr=descr+'dep='+str(f.attribute('dep'))
                        if t[list(t.keys())[0]()][1].count('sidelength')==1:
                            if f.attribute('sidelength')!=None:
                                descr=descr+'sidelength='+str(f.attribute('sidelength'))
                        if t[list(t.keys())[0]()][1].count('dam')==1:
                            if f.attribute('dam')!=None:
                                descr=descr+'dam='+str(f.attribute('dam'))
                    elif type.lower()in ['a','r']:
                        if f.attribute('area2')==None:
                            descr= descrbasis+ ' MaxArea='+ str(f.attribute('area1'))+'\n'
                        else:
                            descr= descrbasis+ ' MaxArea='+ str(f.attribute('area1'))+'*'+str(f.attribute('area2'))+'\n'
                    else:
                        print(type.lower())
                    self.Layer.changeAttributeValue(f.id(),fieldind, descr)
        self.Layer.commitChanges()

    def setLayout(self):
        import VectorStyle
        typelist=[]
        for t in self.Types:
            typekey = list(t.keys())[0]
            typelist.append([typekey,t[typekey],t[typekey][2]])
        #return typelist
        VectorStyle.VectorStyleCaterogized(self.Layer).setMakeFinelMesh(typelist)

class MakeTriangleGrid:
    """ class voor het maken matlab-script maketrianglegrid.m """
    def __init__(self,project,pad,kmllaagnaam,mtgversie,*arg,**varargin):
        """"input: 
            project: naam project, string, bijvoorbeeld: 'test'
            pad: pad waar output m-files geplaatst worden en kml-laagnaam staat,  string-pad, bijvoorbeeld: 'test.kml'
            kmllaagnaam: filenaam waar output m-files geplaatst worden, string-pad
            mtgversie: naam SvaTriangle versie, string, bijvoorbeeld: 'Triangle_3_beta'
            *arg = overeenkomend essentiele argumenten matlab-script make_triangle_grid. Deze zijn afhankelijk van versie SvaTriangle
            **varargin = overeenkomend optional argumenten matlab-script make_triangle_grid. Deze zijn afhankelijk van versie SvaTriangle
        """
        self.Template_param={'$PAD':pad,'$KML':kmllaagnaam,'$MESH':project }
        self.Mfile=os.path.join(pad,'maketrianglegrid.m')
        
        self.Versionsavailable=('Triangle','Triangle_2_beta','Triangle_3_beta')
        self.Arg=arg
        self.Varargin=varargin
        assert(self.Versionsavailable.count(mtgversie)),'onbekend matlab SvaTriangle versie '+str(self.Versionsavailable)
        self.Version=mtgversie
        self.checkarginMtg()
        triangleargin=self.getarginMtg()
        self.E2=triangleargin['E2']

        #self.Template_mfile='Y:/Prog/python/modules/Qgis/maketrianglegrid_template.m' 
        #self.Kml2triangle='Y:\Prog\python\modules\Qgis\kml2triangle_struct_qgis.m'
        self=readMFMconf(self,readMFMconffile,'MakeTriangleGrid')
        
    def getarginMtg(self):
        """ extra inputparameters voor make_triangle_grid"""
        Version=self.Version
        if Version=='Triangle':
            arg=[int] #maxarea 
            varargin={'sqrt_interp':bool,'extra_area_it':bool, 'no_internal':bool,'min_tri_angle':float,'griddata_opt':bool}
            E2=''
        elif Version=='Triangle_2_beta':
            arg=[]
            varargin={'global_maxarea':float,'remove_internals':bool,'min_tri_angle':float,'showpoly':bool,'max_interations':int}
            E2=''
        elif Version=='Triangle_3_beta':
            arg=[]
            varargin={'global_maxarea':float,'remove_internals':bool,'min_tri_angle':float,'showpoly':bool,'max_interations':int,'area_iterations':int}
            E2='E2,'
        else:
            raise ValueError#, 'Versie klopt niet'+self.Version
        triangleargin={'Version':Version,'varargin':varargin,'arg':arg,'E2':E2}
        return triangleargin

    def printarginMtg(self):
        argumenten=self.getarginMtg()
        print('Argument')
        for a in argumenten['arg']:
            print('\t'+str(a)+ '\n')
        print('Varargin')
        for a in argumenten['varargin']:
            print('\t'+ str(a) + ': ' +str(argumenten['varargin'][a]))
        
        
    def checkarginMtg(self):
        """ controleer invoer voor make_triangle_grid"""
        print('Start check invoerparameters in matlab script')
        argin=self.getarginMtg()
        x=0
        if len(self.Arg)<len(argin['arg']):
            if len(self.Varargin)!=0:
                raise TypeError#, 'moet ook argumenten opgeven#, als je varargin opgeeft'
        for a in self.Arg:
            print(a)
            try:
                argin['arg'][x](a)
            except IndexError:
                raise IndexError#, 'Incorrect aantal invoerparameters voor arg:'+str(len(self.Arg))
            x=x+1

        print('Check varargin')
        for v in self.Varargin.iterkeys():
            if argin['varargin'].has_key(v)==False:
                self.printarginMtg()
                raise AttributeError#,'arg: onbestaande keyword '+v
            try:
                argin['varargin'][v](self.Varargin[v])
            except:
                raise ValueError#, 'arg: incorrect ' +str(type(self.Varargin[v]))+ ' voor '+ v
        print('Check invoerparameters  matlab script Succesvol!')

    def setarginMtg(self,line):
        """ aanpassen in een string """
        argtxt=''
        for a in self.Arg:
            argtxt=argtxt+','+str(a)
        varargtxt='' 
        for v in self.Varargin.iterkeys():
            varargtxt=varargtxt+','+'\''+v+'\','+str(self.Varargin[v])
        e2txt=self.E2
        #return argtxt,varargtxt
        line=line.replace( '$ARG',argtxt)
        line=line.replace( '$VARARGIN',varargtxt)
        line=line.replace( '$E2',e2txt)
        return line

    def epsg2matlabcrs(self,epsg):
        """Subfunctie: omzetten epsg code naar een coordinatensysteem voor matlab"""
        if isinstance(epsg,int):
            epsg2matlab={
                0:'wgs84',
                28992:'RD',
                4326:'UTM',#4326:'wgs84',
                32631:'UTM',
                32630:'UTM',
                4263:'minna_badagry',
                2136:'tema',
                #3857:'wgs84',#3857:'UTM',#6326:'wgs84',
            }
        try:
            Matlabcrs=epsg2matlab[epsg]
        except KeyError:
            Matlabcrs='UTM'
        
        print('Nieuwe laag wordt weggeschreven in '+Matlabcrs )
        if Matlabcrs=='UTM':
            print('in QGIS crs van de laag mogelijk aanpassen!!')
        return Matlabcrs

    def makemfileMtg(self,imp_exp,epsg):
        """maak mfile waarmee in matlab en triangle een grid gemaakt wordt."""
        self.Template_param['$IMP_EXP']=imp_exp
        matlabcrs=self.epsg2matlabcrs(epsg)
        self.Template_param['$CRS']=matlabcrs
        g=open(self.Template_mfile,'r')
        text=g.readlines() 
        g.close()
        #check op versie make_triangle_grid
        self.checkarginMtg()
        h=open(self.Mfile,'w')
        for line in text:
            for par in self.Template_param:
                line=line.replace( par,self.Template_param[par])
            line=self.setarginMtg(line)
            line=line.replace( '$TRI' ,self.Version)
            if imp_exp=='imp':
                line=line.replace( 'E2' ,'')
                print('NOODGREEP!')
            h.writelines(line+'\n')
        h.close()

class Mesh(TriangleInvoerLijn,TriangleInvoerPunt,MakeTriangleGrid):
    """ Class voor het maken van een mesh met Triangle
    Dat verloopt in 3 stappen: 
    A) Maak mfile(Function: makeMesh, sub: makemfileMesh)
    B) Start Matlab (Function: makeMesh, sub:startmatlabMesh )
    C) Plot resultaat naar scherm (Function: integraalMesh)
    """

    def __init__(self,project, werkpad,triangleinvlijn,triangleinvpunt=None):
        """ 
        project: stamnaam mesh.out bestand (string)
        werkpad: directory (string), mesh-.out bestand wordt hier neergezet. 
        triangleinvlijn: 3 opties. 
            1) vectorlaag gemaakt met Trianglenvoer
            2) class instance Triangleinvoer
            3) string: laag met naam zoals in de legenda getoond.
        triangleinvpunt: zie triangleinvlijn
        """
        #from qgis.core import QGis
        #import Layers
        TriangleInvoerLijn.__init__(self,project,werkpad)
        inputtype,laag_lijn=self.returntypeinvoerTriangleinvoer(triangleinvlijn,'LineString')
        if inputtype==1:
            result_append=self.appendTriangleinvoer(triangleinvlijn)
        if inputtype==2:
            result_append=self.appendTriangleinvoer(triangleinvlijn.Layer)
        if inputtype==3:
            result_append=self.appendTriangleinvoer(laag_lijn)
        assert (result_append),('Toevoegen laag niet geslaagd \n'+ 
                'Maak eerst Triangleinvoer-objec aan, voordat je Mesh doet.')
        assert(self.hasfieldsTriangleinvoer()),'Laag is geen Triangleinvoerlaag'
        assert(self.hasnullTriangleinvoer()==False),self.Layer.name()+ ' heeft Null waarden op plaatsen waar wel een waarde verwacht wordt.'

        assert(result_append),('Toevoegen laag niet geslaagd \n'+ 
            'Maak eerst Triangleinvoer-objec aan, voordat je Mesh doet.')

        self.Layer.commitChanges() # LET OP TOEGEVOEGD VANWEGE PROBLEMEN MET EGSCHRIJVEN NAAR ATTRIBUUT KML. 
        self.exportTriangleinvoer('kml')#Voor de zekerheid
        kmllijnnaam=self.Filaagnaam

        if triangleinvpunt!=None:
            TriangleInvoerPunt.__init__(self,project,werkpad)
            #onderstaande is kunstgreep, om door appendTriangleinvoer te komen!!!
            self.setLayout=TriangleInvoerPunt(project,werkpad).setLayout
            inputtype,laag=self.returntypeinvoerTriangleinvoer(triangleinvpunt,'Point')
            #print(inputtype)
            #print(triangleinvpunt)

            if inputtype==1:
                result_append=self.appendTriangleinvoer(triangleinvpunt)
            if inputtype==2:
                result_append=self.appendTriangleinvoer(triangleinvpunt.Layer)
            if inputtype==3:
                result_append=self.appendTriangleinvoer(laag)

            assert(result_append),('Toevoegen laag niet geslaagd \n'+ 
                'Maak eerst Triangleinvoer-objec aan, voordat je Mesh doet.')
            assert(self.hasnullTriangleinvoer()==False),self.Layer.name()+ ' heeft Null waarden op plaatsen waar wel een waarde verwacht wordt.'
            kmlpuntnaam=self.Filaagnaam
            self.Layer.commitChanges() # LET OP TOEGEVOEGD VANWEGE PROBLEMEN MET WEGSCHRIJVEN NAAR ATTRIBUUT KML. 
            self.exportTriangleinvoer('kml')#Voor de zekerheid
            self.Kmlfilenaam=project
            self.combinepuntlijnMesh(os.path.join(self.Pad,kmlpuntnaam)+'.kml',os.path.join(self.Pad,kmllijnnaam)+'.kml')
            self.Layer=laag_lijn #NOODZAKELIJK VOOR CORRECT BEREKENEN VAN DE UTM ZONE

        else:
            self.Kmlfilenaam=kmllijnnaam
            """
            Meshatr=readMFMconf(readMFMconffile,'Mesh')
            for m in Meshatr:
                setattr(self,m,Meshatr[m])
            print(dir(self))
            """
        self=readMFMconf(self,readMFMconffile,'Mesh')

        #Laatste Check link naar Matlab-executable 
        assert(os.path.isfile(self.Matlabexec)),'matlab executable bestaat niet:\n'+ self.Matlabexec

    def combinepuntlijnMesh(self,filekmlpunt,filekmllijn):
        """Vrij rudimentaire manier om een puntlaag en een lijnen laag in 1 kml te krijgen."""
        print('Combineer kml lijn en punt ')
        flag_pms='<Placemark>'
        flag_pme='</Placemark>'

        l=open(filekmllijn,'r')
        ltext=l.read()
        l.close()
        p=open(filekmlpunt,'r')
        ptext=p.read()
        p.close()

        i=ltext.rfind(flag_pme)+len(flag_pme)
        j1=ptext.find(flag_pms)
        j2=ptext.rfind(flag_pme)+len(flag_pme)
        
        textcombine=ltext[0:i]
        textcombine=textcombine+'</Folder><Folder><name>trinp_punt</name>'
        textcombine=textcombine+ptext[j1:j2]
        textcombine= textcombine+ltext[i+1:]

        c=open(os.path.join(self.Pad,self.Kmlfilenaam)+'.kml','w')
        c.write(textcombine)
        print('nieuwe kmll'+ os.path.join(self.Pad,self.Kmlfilenaam))

    def startmatlabMesh(self):
        """roep maketrianglegrid in matlab aan """
        from subprocess import call#,check_call
        import shutil
        print('maketrianglegrid.m wordt gezet in ' +self.Pad)
        shutil.copy(self.Kml2triangle,self.Pad)
        switch =' -wait -nojvm -nosplash -r '
        commando='\"run(\''+os.path.join(self.Pad,'maketrianglegrid.m')+'\');exit\"'
        print('start: '+self.Matlabexec+switch+commando)
        ec=call(self.Matlabexec+switch+commando)
        #Voorbeeld:
            #ec=call('C:/\Program Files (x86)/MATLAB/R2007b/bin/matlab.exe -wait -nojvm -nosplash -r
            #run(\'C:    \Users\mro\Documents\MATLAB\make_finelmodel.m\');exit')
        print('einde: '+self.Matlabexec+switch+commando)

    def makeMesh(self,imp_exp,mtgversie,wgs84=False,*arg,**varargin):
        """Hoofdfunctie: maak sepran-grid (.out) uit qgis finelinvoerlaag (met matlab) 
        A)makemfileMesh, B) startmatlabMesh 
         """
        MakeTriangleGrid.__init__(self,self.Project,self.Pad,self.Kmlfilenaam,mtgversie,*arg,**varargin)
        print(wgs84)
        assert type(wgs84)==bool,"incorrecte input voor wgs84: gewenst is True of False.\n Opgegeven is: "+str(wgs84)
        if wgs84==False:
            epsg= int(self.Layer.crs().authid().split(':')[1])
        else:
            epsg=0
        self.makemfileMtg(imp_exp,epsg)
        self.startmatlabMesh()

    def plotMesh(self,imp_exp,wgs84=False):
        """Hoofdfunctie: Voeg .out laag toe aan Qgis-interface"""
        def wgs2epsgutm(laag):
            feat=laag.getFeatures()
            lonlat=np.array([])
            for f in feat:
                f_pl=f.geometry().asPolyline()
                
                for v in f_pl:
                    try:
                        lonlat=np.vstack([lonlat,np.array(v)])
                    except ValueError:
                        lonlat=np.hstack([lonlat,np.array(v)])

            lon=lonlat[:,0]
            lat=lonlat[:,1]
            epsg,utmzone=wgs2epsgutmzone(lon,lat)
            return epsg

        if wgs84==True:
            epsg=4326
        else:
            epsglaag= int(self.Layer.crs().postgisSrid())
            matlabcrs=self.epsg2matlabcrs(epsglaag)
            if epsglaag==4326:
                epsg=wgs2epsgutm(self.Layer)

            elif matlabcrs=='UTM':
                if 32600<epsglaag<32661 or 32700<epsglaag<32761:
                    epsg=epsglaag
                else:
                    g=VectorImportExport.VectorImportExport()
                    g.Layer=self.Layer
                    epsg=wgs2epsgutm(g.Layer)
            elif matlabcrs!='UTM':
                epsg=epsglaag
            else:
                raise AttributeError
        meshfile=self.Project+'.out'
        VectorImportExport.ImportFinelpolygon(self.Pad).importMesh(epsg,meshfile,imp_exp,meshtype='sepran')

    def integraalMesh(self,imp_exp,mtgversie,wgs84=False,*arg,**varargin):
        """Hoofdfuctie: Alle stappen in het maken van triangle invoer tot plotten van mesh op het scherm
        makeMesh, plotMesh"""
        try:
            os.remove(os.path.join(self.Pad,self.Project+'.out'))
        except:
            print('nieuw :'+os.path.join(self.Pad,self.Project+'.out') )

        self.makeMesh(imp_exp,mtgversie,wgs84,*arg,**varargin)     #Maak Mesh.out 
        self.plotMesh(imp_exp,wgs84)                            #plot .out-file in Qgis
