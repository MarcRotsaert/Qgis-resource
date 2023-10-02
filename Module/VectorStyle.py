""" 21-5-2016:
Python module voor styleren van velden 

"""

#class VectorStyle:

from PyQt5.QtGui import QColor#from PyQt4.QtGui import QColor
from qgis.utils import iface 
#from qgis.core import QgsGraduatedSymbolRendererV2,QgsCategorizedSymbolRendererV2,QgsStyleV2,QgsField,QgsGradientStop, QgsVectorLayer#,QGis,
from qgis.core import QgsGraduatedSymbolRenderer,QgsCategorizedSymbolRenderer,QgsStyle,QgsField,QgsGradientStop,QgsVectorLayer,QgsRenderContext

def updateLayerview(layer):
    """
    INPUT:
        - layer: QgsVectorLayer/-object
    """
    if iface.mapCanvas().isCachingEnabled():
        #qgis3 nog niet bevestigd 
        #layer.setCacheImage(None)
        iface.mapCanvas().clearCache()
    else:
        iface.mapCanvas().refresh()
    layer.triggerRepaint()
    #qgis3 nog niet bevestigd 
    #iface.legendInterface().refreshLayerSymbology(layer)
    
def checkFieldname(layer,fieldstr):
    """
    INPUT:
        - fieldstr = naam van veld(field) dat geplot moet worden (STRING)
    """
    availablefields=[str(f.name()) for f in layer.dataProvider().fields()]
    assert(layer.dataProvider().fields().indexFromName(fieldstr)>=0), fieldstr +' is een verkeerd Veld opgegeven. Beschikbare velden bij laag zijn:'+ str(availablefields)

class VectorStyleColorramp:
    """ Styleren van kleurenveld
    Hoofdfunctions: 
    colorramp.... = plotten van veld
    INPUT:
        - layer: QgsVectorLayer-object
    """
    def __init__(self,layer):
        assert(isinstance(layer,QgsVectorLayer)) 
        self.Layer=layer
        #self.myRenderer=QgsGraduatedSymbolRendererV2()
        self.myRenderer=QgsGraduatedSymbolRenderer()

    def setColorrampName(self,myRenderer,colorrampname,invertcr=True):
        """ 
        Instellen van colorramp (=colormap)
        INPUT:
            -myRenderer: 
            - colorrampname= naam van colorramp, overeenkomend met colormap in matlab (STRING).
            - invertcr= colorramp in omgekeerde volgorde. (BOOL) 
        OUTPUT:
            (rendererV2-OBJECT) 
        """

        #myStyle = QgsStyleV2().defaultStyle()
        myStyle = QgsStyle().defaultStyle()
        defaultColorRampNames = myStyle.colorRampNames()
        #try: 
        ind=defaultColorRampNames.index(colorrampname)
        #print ind
        ramp = myStyle.colorRamp(defaultColorRampNames[ind])
        #except ValueError:
        #ramp =self.setColorrampCptCity(colorrampname)
        #myRenderer.updateColorRamp(ramp,inverted=invertcr)
        

        if invertcr is True:
            ramp.invert()
        #self.myRenderer.updateColorRamp(ramp,inverted=invertcr)
        self.myRenderer.updateColorRamp(ramp)
        
        updateLayerview(self.Layer)
        return myRenderer
    """ 
    Onderstaande voorlopig niet geimplementeerd: 
    zie plugin:    svg2color voor mogelijke wijze van implementatie. 
    Nu nog voor mij te ingewikkeld.
    
    def setColorrampCptCity(self,naam):
        
        from qgis.core import QgsCptCityColorRampV2
        cr=QgsCptCityColorRampV2(naam).clone()
        return cr
        #self.myRenderer.setSourceColorRamp(cr)
        #self.Layer.setRendererV2(self.myRenderer)
    """

    def setBordertransparent(self,transparent=True):
        """ Zet rand op transparant of zwart
        INPUT: 
            transparent I/O (BOOL)
        """
        
        #myRenderer=self.Layer.rendererV2()
        myRenderer=self.Layer.renderer()
        #for symbol in myRenderer.symbols():
        #
        #for sl in myRenderer.symbols().symbolLayers():
        for symbol in myRenderer.symbols(QgsRenderContext()):
            sl=symbol.symbolLayer(0)
            try:
                if transparent==True:
                    #sl.setBorderColor(QColor(255,255,255,0))
                    sl.setStrokeColor(QColor(255,255,255,0))
                elif transparent==False: 
                    #sl.setBorderColor(QColor(0,0,0,255))
                    sl.setStrokeColor(QColor(0,0,0,255))
            except:
                pass

    def colorrampEqualinterval(self,fieldstr,nr_classes,colorrampname='Spectral',invertcr=True):
        """ Plot Kleurenveld. Qgis bepaald setBorderColorklassengrenzen. 
        intervallen tussen klassengrenzen zijn voor alle klassen gelijk. 
        INPUT:
        - fieldstr = naam van veld(field) dat geplot moet worden (STRING)
        - nr_classes= het aantal klasseintervallen (INTEGER)
        - colorrampname= naam van colorramp, overeenkomend met colormap in matlab (STRING). 
            Voor lijst beschikbare colorramps:
                QgsStyleV2().defaultStyle().colorRampNames() 
        - invertcr= colorramp in omgekeerde volgorde. (BOOL) 
        """
        checkFieldname(self.Layer,fieldstr)
        self.myRenderer.setClassAttribute(fieldstr)
        #self.myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
        self.myRenderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
        #self.myRenderer.updateClasses(self.Layer,QgsGraduatedSymbolRendererV2.EqualInterval,nr_classes)
        self.myRenderer.updateClasses(self.Layer,QgsGraduatedSymbolRenderer.EqualInterval,nr_classes)
        self.myRenderer=self.setColorrampName(self.myRenderer,colorrampname,invertcr)
        #self.Layer.setRendererV2(self.myRenderer)
        self.Layer.setRenderer(self.myRenderer)
        self.setBordertransparent()
        updateLayerview(self.Layer)

    def colorrampRanges(self,fieldstr,rangelimits,colorrampname='Spectral',invertcr=True):
        """ Plot Kleurenveld. Bepaal zelf klassen grenzen.
        INPUT:
        - fieldstr = naam van veld (field) dat geplot moet worden  (STRING)
        - rangelimits = grenzen tussen klassen. Wordt opgegeven als een reeks waarden (LIST met INTEGER/FLOAT), 
                Bijvoorbeeld: [-1,0,2,10,1000] of  range(0,10,2) of numpy.arange(-2.5,2.5,0.25)
        - colorrampname= naam van colorramp, overeenkomend met colormap in matlab (STRING). 
            Voor lijst beschikbare colorramps:
                QgsStyleV2().defaultStyle().colorRampNames() 
        - invertcr= colorramp in omgekeerde volgorde. (BOOL) 
         """
        checkFieldname(self.Layer,fieldstr)

        self.myRenderer.setClassAttribute(fieldstr)
        #self.myRenderer.setMode(QgsGraduatedSymbolRendererV2.Custom)
        self.myRenderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        #self.myRenderer.updateClasses(self.Layer,QgsGraduatedSymbolRendererV2.EqualInterval,len(rangelimits)-1)
        self.myRenderer.updateClasses(self.Layer,QgsGraduatedSymbolRenderer.EqualInterval,len(rangelimits)-1)

        for a in range(len(rangelimits)-1):
            self.myRenderer.updateRangeLowerValue(a,rangelimits[a])
            self.myRenderer.updateRangeUpperValue(a,rangelimits[a+1])
        self.myRenderer=self.setColorrampName(self.myRenderer,colorrampname,invertcr)
        #self.Layer.setRendererV2(self.myRenderer)
        self.Layer.setRenderer(self.myRenderer)
        self.setBordertransparent()
        updateLayerview(self.Layer)
    
    #class VectorStylePolygon(VectorStyle):
        #assert (QGis.WKBPolygon==layer.wkbType()), 'Invoerlaag is geen Polygon-laag'

class VectorStyleCaterogized:
    def __init__(self,layer):
        assert(isinstance(layer,QgsVectorLayer)) 
        self.Layer=layer
        #self.myRenderer=QgsCategorizedSymbolRendererV2
        self.myRenderer=QgsCategorizedSymbolRenderer
    
    def setSimpleline(self,table,setattr=None):
        import Fields as Fi
        from qgis.core import QgsLineSymbol,QgsRendererCategory
        """
        Eenvoudige  renderer voor een lijn 
        Input:table = input voor renderer, kleur linebreedte en naam in legenda
                    attr val  ["r,g,b" ,        linewidth, legenda],
        table = {   'buis':     ["243, 186, 61", 0.4, 'buis'],
                    'overig' : ["221, 35, 54",  0.4m, 'overige leiding'],
                    'riool' : ["149, 110, 59",  0.4, 'riolering'],
                    'water' : "53, 125, 225",   0.4, 'waterleiding'],
                    'spanning' : "74, 235, 219",0.4, 'electriciteit, laag'],
                    'datatransport' : "51, 160, 44", 0.4, 'transport' ]
                    'gas hoge druk':"243, 186, 61", 0.4, 'gas hoog' ]
                    'gas lage druk':"246, 255, 74", 0.4, ' gas laag' ]
                }
                setattr = Attribuut waartegen waarden uitgezet worden
        """

        if setattr==None:
            self.myRenderer=self.Layer.renderer()
            setattr = self.myRenderer.classAttribute()
        i_field = Fi.indexFieldname(self.Layer,setattr)
        uniqueattr = self.Layer.uniqueValues(i_field)

        for val in table:
            if val not in uniqueattr and val!=None:
                print('attribuut waarde ' +val + ' niet voor lijn gedefinieerd')
        categories=[]
        for val in table:
            rgb = str(table[val][0])
            lw = table[val][1]
            leg = table[val][2]
            sym_b=QgsLineSymbol().createSimple({'width' : str(lw),'color' :rgb})
            categories.append(QgsRendererCategory(val, sym_b, leg))
        if None not in table:
            sym_b=QgsLineSymbol().createSimple({'width' : str(0.2),'color' :"122,122,122"})
            categories.append(QgsRendererCategory(None, sym_b, ''))
            print('no')
        #return self,categories
        #ren = self.myRenderer
        
        ren = QgsCategorizedSymbolRenderer("",categories)
        self.myRenderer = ren
        #ren = QgsCategorizedSymbolRenderer("",categories)
        if setattr!=None:
            self.myRenderer.setClassAttribute(setattr)
        self.Layer.setRenderer(self.myRenderer)
        updateLayerview(self.Layer)
    
    def setMakeFinelMesh(self,typelist):
        """opmaken van een triangleinvoerlaag aan hand van type
        Nog aanpassen voor Qgis3!!!!!!!
        """
        #from qgis.core import QgsLineSymbolV2,QgsCategorizedSymbolRendererV2,QgsRendererCategoryV2
        from qgis.core import QgsLineSymbol,QgsCategorizedSymbolRenderer,QgsRendererCategory
        import Layers
        assert (Layers.returnVectorLayerGeometryType(self.Layer)=='LineString')
        categories=[]
        for t in typelist:
            #sym_b=QgsLineSymbolV2().createSimple({'width' : '1.0','color' :t[2]})
            sym_b=QgsLineSymbol().createSimple({'width' : '1.0','color' :t[2]})
            #sym_h=QgsLineSymbolV2().createSimple({'width' : '1.0','color' :"0,255,0"})
            #sym_a=QgsLineSymbolV2().createSimple({'width' : '1.0','color' :"0,0,255"})
            #sym_i=QgsLineSymbolV2().createSimple({'width' : '1.0','color' :"125,125,0"})
            #categories.append(QgsRendererCategoryV2(t[0], sym_b,t[1]))
            categories.append(QgsRendererCategory(t[0], sym_b, t[1][0]))
            #categories.append(QgsRendererCategory().setSymbol(sym_b))
            #categories.append(QgsRendererCategoryV2("h", sym_h,"hole"))
            #categories.append(QgsRendererCategoryV2("a", sym_a,"area"))
            #categories.append(QgsRendererCategoryV2("i", sym_i,"internal"))

        #sym_overig=QgsLineSymbolV2().createSimple({'width' : '1.0','color' :"0,0,0",'penstyle':'dash'})
        sym_overig=QgsLineSymbol().createSimple({'width' : '1.0','color' :"0,0,0",'penstyle':'dash'})
        #categories.append(QgsRendererCategoryV2('',sym_overig,'fout'))
        categories.append(QgsRendererCategory('',sym_overig,'fout'))
        #self.myRenderer=QgsCategorizedSymbolRendererV2("",categories)
        #ren=self.myRenderer("",categories=categories)
        print(categories)
        ren=self.myRenderer('1',categories=categories)
        ren.setClassAttribute('type')
        #self.Layer.setRendererV2(ren)
        self.Layer.setRenderer(ren)
        updateLayerview(self.Layer)