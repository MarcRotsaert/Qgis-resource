""" Verzameling functies om eenvoudig info over lagen op te zoeken, Lagen te selecteren en te manipuleren"""

from qgis.utils import iface
from qgis.core import QgsProject
from qgis.core import QgsWkbTypes
from qgis.core import QgsRasterLayer,QgsVectorLayer, QgsVectorFileWriter
import os

def _python3getlayerslist():
    li = [layer for layer in QgsProject.instance().mapLayers().values()]
    return li
def _python3getnodeslist():
    nodes = QgsProject.instance().layerTreeRoot().children()
    return nodes

def returnVectorLayerGeometryType(layer):
    if layer.geometryType()==QgsWkbTypes.PointGeometry:
        return 'Point'
    elif layer.geometryType()==QgsWkbTypes.LineGeometry:
        return 'LineString'
    elif layer.geometryType()==QgsWkbTypes.PolygonGeometry:
        return 'Polygon'
    else:
        #raise TypeError#, 'Complex laagtype die niet behoort tot hoofdgroep Punt, Lijn of Polygoon'
        raise TypeError('layer behoort tot complex laagtype, niet tot hoofdgroep Punt, Lijn of Polygoon')


def checkVectorLayerGeometryType(layer,strgeometrytype):
    #from qgis.core import QGis
    geometries=['Point','LineString','Polygon']
    assert(geometries.count(strgeometrytype)),'Invoer voor geometries: '+str(strgeometrytype)
    if strgeometrytype=='Point':
        #check=QGis.Point
        check=QgsWkbTypes.PointGeometry
    elif strgeometrytype=='LineString':
        #check=QGis.Line
        check=QgsWkbTypes.LineGeometry
    elif strgeometrytype=='Polygon':
        #check=QGis.Polygon
        check=QgsWkbTypes.PolygonGeometry
    else:
        raise TypeError('Mag eigenlijk niet gebeuren. Check code op inconsistenties')
    result=layer.geometryType()==check
    return result


def returnLayersbyname(laagnaam):
    """
    Input: naam laag, string, 
    Output: list (met QgsLayers-object)
    """
    #li=iface.legendInterface()a
    layersbyname=[]
    li=_python3getlayerslist()
    #for l in li.layers():
    for l in li:
        if l.name()==laagnaam:
            layersbyname.append(l)
    if layersbyname==[]:
        print('GEEN LAAG GEVONDEN')
    return layersbyname


def returnLayersselected():
    """
    Input: None
    Output: Qgs Layer """
    #li=iface.legendInterface()
    #selectielagen=li.selectedLayers()
    tv = iface.layerTreeView()
    selectielagen = tv.selectedLayers()
    return selectielagen

def returnLayersvisible(visible=True):
    """        Lijst met Lagen die zichtbaar (visible=True) of onzichtbaar (visible=False) zijn
    Input Boolean, 
    Output: Lijst met Qgs Layer,  """

    visiblelayers=[]
    invisiblelayers=[]

    li=_python3getlayerslist()
    tr = QgsProject.instance().layerTreeRoot()
    #for l in li.layers():
    #    if li.isLayerVisible(l):
    for l in li:
        #print(tr.findLayer(l.id()).isVisible())
        if tr.findLayer(l.id()).isVisible():
            visiblelayers.append(l)
        else:
            invisiblelayers.append(l)
    if visible==True:
        return visiblelayers
    else:
        return invisiblelayers
    
    """
    li=iface.legendInterface()
    for l in li.layers():
        print(li.isLayerVisible(l))
        if li.isLayerVisible(l):
            visiblelayers.append(l)
        else:
            invisiblelayers.append(l)
    if visible==True:
        return visiblelayers
    else:
        return invisiblelayers
    """
    
def returnGroupsvisible(visible=True):
    """Lijst met Groepen die zichtbaar (visible=True) of onzichtbaar (visible=False) zijn
        Input Boolean, 
        Output: Lijst met Qgs Layer (nee! klopt niet!).  Hier moet nog aan gesleuteld worden!!!!!!!!!""" 
    visiblegroups=[]
    invisiblegroups=[]

    nodes = _python3getnodeslist()
    for n in nodes:
        if n.nodeType() == 0:
            if n.isVisible():
                visiblegroups.append(n)
            else:
                invisiblegroups.append(n)
    
    """li=iface.legendInterface()
    for ind_g in range(len(li.groups())):
        if li.isGroupVisible(ind_g):
            print 
            visiblegroups.append(li.groups()[ind_g])
        else:
            invisiblegroups.append(li.groups()[ind_g])
    """
    
    if visible==True:
        return visiblegroups
    else:
        return invisiblegroups

def setLayervisible(name,IO=True):
    """ maak laag zichtbaar: 
        Input naam laag (String), zichtbaar maken (True), onzichtbaar maken (False) (Boolean) 
        Output: Lijst met Qgs Layer
    """
    #li=iface.legendInterface()
    #for l in li.layers():
    #    if l.name()==name:
    #        li.setLayerVisible(l,IO)
    li=_python3getlayerslist()
    for l in li:
        if l.name()==name:
            QgsProject.instance().layerTreeRoot().findLayer(l.id()).setItemVisibilityChecked(IO)
    #        li.setLayerVisible(l,IO)
    iface.mapCanvas().refresh()
    
def setLayername(name,layer=None):
    if layer==None:
        layer=iface.activeLayer()
    else:
        print(type(layer))
        assert(isinstance(layer,QgsRasterLayer)|isinstance(layer,QgsVectorLayer))
    #layer.setLayerName(name)
    layer.setName(name)

def reprojectLayer(layer, epsg,filenaam,pad):
    """ zet coordinaten uit kaartlaag om naar een andere coordinatenstelsel ahv epsg waarde"""
    import processing
    tempfilein=os.path.join(pad,filenaam)
    QgsVectorFileWriter.writeAsVectorFormat(layer,tempfilein,None,None) 
    fileuit=filenaam+'_reproj.shp'
    tempfileuit=os.path.join(pad,fileuit)
    processing.runalg('qgis:reprojectlayer',tempfilein,'epsg:'+str(epsg),tempfileuit)
    return tempfileuit

def makeTemplayer(Type):
    assert Type in ['Point','LineString','Polygon']
    layer=QgsVectorLayer(Type+'?', "temporary_"+Type.lower()+"s", "memory")
    QgsProject.instance().addMapLayer(layer)
    
    return layer

def removeLayer(layer):
    """
    Input: QgsLayer object
    """
    QgsProject.instance().removeMapLayers([layer.id()])

def exportShape(fname, path,layer):

    import os
    print
    QgsVectorFileWriter.writeAsVectorFormat(layer,os.path.join(path,fname),"utf-8",layer.crs(),"ESRI Shapefile")
    print('created:'+os.path.join(path,fname))
    
