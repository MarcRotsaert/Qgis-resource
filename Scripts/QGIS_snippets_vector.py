#TOEVOEGEN temporary laag  aan project
layertypes = ['LineString','Point', 'Polygon']
for la_type in layertypes:
    la=QgsVectorLayer(la_type,'laagnaam','memory')
    QgsProject.instance().addMapLayer(la)

#____________________________________________________________________________________________
#BUFFER rond lijn
#processing-toolbox in scripting
from qgis import processing
path_out = r'D:\TEMP'
# 1) Maak buffer
print('Stap 1: maak buffer rond lijn')

filein= r'D:/TEMP/Qgis/voorbeeldbestanden/overig/Lijnen.shp'
file_buffer = 'Buffered_2.shp'
fileout = os.path.join(path_out,file_buffer)

buffer_input ={ 
	'DISSOLVE' : False, 
    'DISTANCE' : 60, 
    'END_CAP_STYLE' : 2, 
    'INPUT' : filein, 
    'JOIN_STYLE' : 0, 
    'MITER_LIMIT' : 2, 
    'OUTPUT' : fileout, 
    'SEGMENTS' : 5 }
processing.run("gdal:buffervectors",buffer_input)
la_buffer = QgsVectorLayer(fileout)
qgsproject.addMapLayer(la_buffer)
#____________________________________________________________________________________________
# Bereken richting lijn
la = Layers.returnLayersbyname('Lijnen')[0]
import vector            
for feat in la.getFeatures():
	geom = feat.geometry()
	beginpunt = geom.get()[0]
	eindpunt = geom.get()[-1]
	dx = eindpunt.x()-beginpunt.x()
	dy = eindpunt.y()-beginpunt.y()
	degn = vector.degn_cart2naut_gt(dx,dy)

#____________________________________________________________________________________________
# Bereken richting lijn 2
import vector # eigen module
ix_dir = Fields.indexFieldname(la_chain,'angle')
for feat in la_chain.getFeatures():
	geom = feat.geometry()
	punt = geom.get()
	degn = feat.attributes()[ix_dir]
	loodrecht_naut = degn+90
	loodrecht_pol= vector.naut2pol_gt(loodrecht_naut)	

#____________________________________________________________________________________________
# Voeg punt toe aan een laag
z = 10.0
x = 133454.0 
y = 500943.0

fi = QgsField('afstand',QVariant.Double,'',4,1)
qgsfields = QgsFields()
qgsfields.append(fi)
feat = QgsFeature(qgsfields, 0)

qgsp = QgsPoint()
qgsp.setX(float(x))
qgsp.setY(float(y))
feat.setGeometry(qgsp)
feat.setAttributes([z])

iface.activeLayer().addFeatures([feat])
#____________________________________________________________________________________________
# inlezen voorgedefinieerde STYLE. 
lay = iface.activeLayer()
lay.loadNamedStyle(r'style.qml')

#____________________________________________________________________________________________
# Feature EXPRESSIONS
field = '\"OBJECTID_1\"'
expstring = "{}>{} AND {}<={}".format(field,1,field,4)
#expstring = "\"OBJECTID_1\">1 AND \"OBJECTID_1\"<=1"
print(expstring)
exp = QgsExpression(expstring)
featiter = iface.activeLayer().getFeatures(QgsFeatureRequest(exp))
#ander voorbeeld 
themas = [r'%Laags%',r'Middens%',r'%Data%']
for th in themas:
	Fe.selectFeaturesexpr(la,"\"Thema\" LIKE '"+th+'\'')

#____________________________________________________________________________________________
#SELECTEER  features
la_bro = La.returnLayersbyname('Lijnen')[0]
ids=[]
for fe in la_bro.getFeatures():
	ids.append(fe.id())
la_bro.select(ids)


