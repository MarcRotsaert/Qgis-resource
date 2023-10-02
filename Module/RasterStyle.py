""" 21-5-2016:
Python module voor styleren van rasters 
Experimenteel
"""

#class VectorStyle:
from PyQt5.QtGui import QColor#from PyQt4.QtGui import QColor
from qgis.utils import iface 
#from qgis.core import QgsRasterLayer,QgsRasterShader,QgsSingleBandPseudoColorRenderer,QgsColorRampShader,QgsStyleV2 #QgsGraduatedSymbolRendererV2,QgsStyleV2,QgsField,QgsGradientStop,QgsVectorLayer#,QGis,
from qgis.core import QgsRasterLayer,QgsRasterShader,QgsSingleBandPseudoColorRenderer,QgsColorRampShader,QgsStyle #QgsGraduatedSymbolRendererV2,QgsStyleV2,QgsField,QgsGradientStop,QgsVectorLayer#,QGis,

def updateLayerview(layer):
    #if iface.mapCanvas().isCachingEnabled():
    #    layer.setCacheImage(None)
    #else:
    iface.mapCanvas().refresh()
    
    layer.triggerRepaint()
    #iface.legendInterface().refreshLayerSymbology(layer)

def getMinMaxraster(layer):
    layer.dataProvider()
    

class RasterStyleColorramp:
    """ Styleren van kleurenveld
    Hoofdfunctions: 
    colorramp.... = plotten van veld
    """
    def __init__(self,layer):
        assert(isinstance(layer,QgsRasterLayer)) 
        print( 'no' )
        self.Layer=layer
        self.myRenderer=self.Layer.renderer()
        if self.myRenderer.type()!='singlebandpseudocolor':
            rend=QgsSingleBandPseudoColorRenderer(self.Layer.dataProvider(),self.Layer.type())
            bstat=self.Layer.dataProvider().bandStatistics(1)
            print(bstat.minimumValue,bstat.maximumValue)
            
            #self.Layer.setDrawingStyle("SingleBandPseudoColor")
            self.Layer.setRenderer(rend)
            
            #try:
            self.colorrampRanges([bstat.minimumValue, bstat.maximumValue],'Spectral')
            #except:
            #    self.Layer.setDrawingStyle("SingleBandGray")
            #raise AttributeError
            self.Layer.myRenderer=self.Layer.renderer()
            #self.Layer.renderer(rend)
            print('stel kleurenschaal opnieuw in')

    def returnRastershaderColormapDiscrete(self,classlim,colorrampname='Spectral',invertcr=False):
        """ Instellen van colorramp op basis van een minimum en maximum waarde en een voorgedefinieerde colorramp"""
        #myStyle = QgsStyleV2().defaultStyle()
        myStyle = QgsStyle().defaultStyle()
        defaultColorRampNames = myStyle.colorRampNames()
        ind=defaultColorRampNames.index(colorrampname)
        ramp = myStyle.colorRamp(defaultColorRampNames[ind])
        lst=[]
        #for a in range(0,ramp.count()):
        for a,kl in enumerate(classlim):
            val=ramp.value(a)
            #print val
            if invertcr==False:
                qcol=ramp.color(val)
            elif invertcr==True:
                qcol=ramp.color(1-val)
            else:
                raise ValueError
            #valin=minval+(maxval-minval)*val
            valin=kl
            #print valin
            #print col.green()
            lst.append(QgsColorRampShader.ColorRampItem(valin,qcol,str(valin)))

        myColorRamp = QgsColorRampShader()
        myColorRamp.setColorRampItemList(lst)
        #print(lst)

        #myColorRamp.setColorRampType(QgsColorRampShader.DISCRETE)
        #myColorRamp.setColorRampType(QgsColorRampShader.Interpolated)
        myColorRamp.setColorRampType(QgsColorRampShader.Discrete)
        #myColorRamp.setColorRampType(QgsColorRampShader.INTERPOLATED)
        myRasterShader = QgsRasterShader()
        
        myRasterShader.setRasterShaderFunction(myColorRamp)
        #print(dir(myRasterShader))
        #myRasterShader.setColorRampType(QgsColorRampShader.Discrete)
        updateLayerview(self.Layer)
        return myRasterShader#,lst,myColorRamp
            
            
    def returnRastershaderColormap(self,minval,maxval,colorrampname='Spectral',invertcr=False,discrete=False):
        """ Instellen van colorramp op basis van een minimum en maximum waarde en een voorgedefinieerde colorramp"""
        #myStyle = QgsStyleV2().defaultStyle()
        myStyle = QgsStyle().defaultStyle()
        defaultColorRampNames = myStyle.colorRampNames()
        ind=defaultColorRampNames.index(colorrampname)
        ramp = myStyle.colorRamp(defaultColorRampNames[ind])
        lst=[]
        for a in range(0,ramp.count()):
            val=ramp.value(a)
            #print val
            if invertcr==False:
                qcol=ramp.color(val)
            elif invertcr==True:
                qcol=ramp.color(1-val)
            else:
                raise ValueError
            valin=minval+(maxval-minval)*val
            #print valin
            #print col.green()
            lst.append(QgsColorRampShader.ColorRampItem(valin,qcol,str(valin)))

        myColorRamp = QgsColorRampShader()
        myColorRamp.setColorRampItemList(lst)
        print(lst)
        if discrete:
            #myColorRamp.setColorRampType(QgsColorRampShader.DISCRETE)
            myColorRamp.setColorRampType(QgsColorRampShader.Discrete)
        else:
            #myColorRamp.setColorRampType(QgsColorRampShader.INTERPOLATED)
            myColorRamp.setColorRampType(QgsColorRampShader.Interpolated)
        myRasterShader = QgsRasterShader()
        myRasterShader.setRasterShaderFunction(myColorRamp)
        updateLayerview(self.Layer)
        return myRasterShader#,lst,myColorRamp

    def returnRastershaderMinmax(self,minval,maxval):
        sf=self.myRenderer.shader().rasterShaderFunction()
        lst=[]
        minvalold=sf.colorRampItemList()[0].value
        maxvalold=sf.colorRampItemList()[-1].value
        
        for cri in sf.colorRampItemList():
            valueold=cri.value
            #valin=valueold*(maxval-minval)/(maxvalold-minvalold)-(minvalold+minval)
            print((valueold-minvalold)/(maxvalold-minvalold))
            valin=minval+(valueold-minvalold)/(maxvalold-minvalold)*(maxval-minval)
            qcol= cri.color
            lst.append(QgsColorRampShader.ColorRampItem(valin,qcol,str(valin)))
            print(valueold,valin)
        #return lst
        myColorRamp = QgsColorRampShader()
        myColorRamp.setColorRampItemList(lst)
        #if discrete:
        #    myColorRamp.setColorRampType(QgsColorRampShader.DISCRETE)
        #else:
        myColorRamp.setColorRampType(QgsColorRampShader.INTERPOLATED)
        myRasterShader = QgsRasterShader()
        myRasterShader.setRasterShaderFunction(myColorRamp)
        return myRasterShader

    def setTransparentbyvalue(self,minval=None,maxval=None,perctransparent=100):
        from qgis.core import QgsRasterTransparency
        lren=self.Layer.renderer()
        transobj=QgsRasterTransparency()
        if minval==None:
            print('verwijder transparantie')
        else:
            print('Voeg transparantie waarden toe')
            translayer=lren.rasterTransparency()
            if translayer==None:#deze situatie treedt op als je een nieuw kleurenramp (colorrampRanges) hebt geselecteerd
                lren.setRasterTransparency(transobj)
                translayer=lren.rasterTransparency()
            tlist=translayer.transparentSingleValuePixelList()
            print(tlist)
            o=QgsRasterTransparency.TransparentSingleValuePixel()
            o.min=minval
            o.percentTransparent=perctransparent
            if maxval==None:
                maxval=minval
            o.max=maxval
            tlist.append(o)
            print(tlist)
            #transobj=QgsRasterTransparency()
            transobj.setTransparentSingleValuePixelList(tlist)
        lren.setRasterTransparency(transobj)
        updateLayerview(self.Layer)
        return lren

    def colorrampRanges(self,rangelimits,colorrampname='Spectral',invertcr=False,discrete=False):
        
        if discrete==False:
            assert(len(rangelimits)==2),'Geef minimum en maximum op.'
        
            #if colormapname!=None:
            myRasterShader=self.returnRastershaderColormap(rangelimits[0],rangelimits[1],colorrampname,invertcr,discrete)
            #print myRasterShader
            #else:
            #if invertcr==False:
            #myRasterShader=self.returnRastershaderMinmax(rangelimits[0],rangelimits[1])
            #else:
            #myRasterShader=self.returnRastershaderMinmax(rangelimits[0],rangelimits[1])
        else: 
            myRasterShader=self.returnRastershaderColormapDiscrete(rangelimits,colorrampname,invertcr)
        
        rend=QgsSingleBandPseudoColorRenderer(self.Layer.dataProvider(),self.Layer.type(),myRasterShader)
        self.myRenderer=rend
        self.Layer.setRenderer(self.myRenderer)
        updateLayerview(self.Layer)
        return rend
        