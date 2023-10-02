from qgis.core import QgsExpression,QgsFeatureRequest, NULL, QgsWkbTypes
import Layers
import Fields

def addFeaturetolayer(layer,featurelist):
    """
    Voeg features toe aan een laag
    Input:
        layer = vectorlaag object (QgsVectorLayer)
        featurelist = list van feature-objecten) ( 
    """
    assert isinstance(featurelist,list)
    layer.startEditing()
    layer.dataProvider().addFeatures(featurelist)
    layer.commitChanges()
"""
def _selectFeaturesbyFieldvalue(layer, fieldname,selectievalue):
    i_field = layer.fields().indexFromName(fieldname)
    assert i_field!=-1, 'ongeldig fieldname'
    
    selectiefeatures = []
    for f in layer.getFeatures():
        attrvalue = f.attribute(i_field)
        #return attrvalue
        #print(attrvalue)
        #print(selectiefeatures)
        try:
        
            if selectievalue in attrvalue:
                selectiefeatures.append(f)
        except TypeError:
            #print('no')
            continue
    return selectiefeatures
"""

def returnFeaturetype(feat):
    if feat.geometry().type()==QgsWkbTypes.PointGeometry:
        return 'Point'
    elif feat.geometry().type()==QgsWkbTypes.LineGeometry:
        return 'LineString'
    elif feat.geometry().type()==QgsWkbTypes.PolygonGeometry:
        return 'Polygon'
    else:
        #raise TypeError#, 'Complex laagtype die niet behoort tot hoofdgroep Punt, Lijn of Polygoon'
        raise TypeError('layer behoort tot complex laagtype, niet tot hoofdgroep Punt, Lijn of Polygoon')


def returnFeaturesbyfieldvalue(layer, fieldname,selectievalue):
    """
    return list met feature-objecten aan hand van een waarde
    Input: 
        layer = vectorlaag object (QgsVectorLayer)
        fieldnaam = naam van een Field (string)
        selectievalue = waarde van een feature  [string, int, bool, float)
    Output: 
        list met Feature-objecten

    Voorbeelden:
    expression_str = '"Z         " = 2.25'
    """
    i_field = layer.fields().indexFromName(fieldname)
    assert i_field!=-1, 'ongeldig fieldname'

    if isinstance(selectievalue,str):
        valuestr = "\'"+selectievalue+"\'"
        expression_str  ="\""+fieldname+"\"=" + valuestr
    elif selectievalue is NULL:
        valuestr = " is NULL"
        expression_str ="\""+fieldname+"\"  is NULL"
    else:
        valuestr  = str(selectievalue)
        expression_str ="\""+fieldname+"\"=" + valuestr
    #print(expression_str)
    #expression_str = "\""+fn[1]+"\" is 'node12'"
    #expr = QgsExpression("\"SBA proj\" = 'SBA2400'" )
    expr = QgsExpression(expression_str)
    it = layer.getFeatures(QgsFeatureRequest(expr))
    selectiefeatures = [i for i in it]
    #print(expression_str)
    #print(selectiefeatures)
    #return expression_str
    return selectiefeatures

def selectFeaturesexpr(layer,expression_str,invert=False):
    expres = QgsExpression(expression_str)
    layer.selectByExpression(expression_str)
    if layer.selectedFeatureCount()==0:
        print('Warning: no selected features')
    if layer.selectedFeatureCount()==layer.featureCount():
        print('Warning: number of selected features equals total number of features')
    if invert==True:
        layer.invertSelection()
    

def selectFeatureslist(layer,featurelist,invert=False):
    """
    Maak een Qgis selecttie van features 
    Input 
        layer = vectorlaag object (QgsVectorLayer)
        featurelist = list met feature objecten
        invert = omkeren selectie
    Output:

    """

    assert len(featurelist)>0
    
    #try:
    ids =[i.id() for i in featurelist]
    layer.select( ids )
    if invert==True:
        layer.invertSelection()
    #except AttributeError as e: 
    #    print(e.args)

def copyFeaturevaluetoField(layer,featurelist,fieldname_in,fieldname_out):


    fi_in = Fields.FieldProperties(layer,fieldname_in)
    fi_out = Fields.FieldProperties(layer,fieldname_out)
    
    layer.startEditing()
    for feat in featurelist:
        copyval = feat.attributes()[fi_in.returnFieldindex()]
        
        feat.setAttribute(fi_out.returnFieldindex(),copyval)
        layer.updateFeature(feat)
    layer.commitChanges()



def copyFeaturestotemplayer(featurelist,):
    lt = returnFeaturetype(featurelist[0])
    fields = featurelist[0].fields()
    l2 = Layers.makeTemplayer(lt)
    l2.startEditing()
    dp = l2.dataProvider()
    dp.addAttributes(fields)
    dp.addFeatures(featurelist)
    l2.commitChanges()
    return l2


