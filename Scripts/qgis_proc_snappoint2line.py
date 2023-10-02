from shapely.wkt import *
from shapely.geometry import *
from qgis.gui import *
from PyQt4.QtCore import Qt
lineLayer = iface.mapCanvas().layer(0)
pointLayer =  iface.mapCanvas().layer(1)
canvas =  iface.mapCanvas()
spIndex = QgsSpatialIndex() #create spatial index object
lineIter =  lineLayer.getFeatures()
for lineFeature in lineIter:
    spIndex.insertFeature(lineFeature)        
pointIter =  pointLayer.getFeatures()


for feature in pointIter:
    ptGeom = feature.geometry()
    pt = feature.geometry().asPoint()
    nearestIds = spIndex.nearestNeighbor(pt,1) # we need only one neighbour
    featureId = nearestIds[0]
    nearestIterator = lineLayer.getFeatures(QgsFeatureRequest().setFilterFid(featureId))
    nearFeature = QgsFeature()
    nearestIterator.nextFeature(nearFeature)
    shplyLineString = loads(nearFeature.geometry().exportToWkt())
    shplyPoint = loads(ptGeom.exportToWkt())
    #nearest distance from point to line
    dist = shplyLineString.distance(shplyPoint)
    print(dist)
    #the point on the road where the point should snap
    shplySnapPoint = shplyLineString.interpolate(shplyLineString.project(shplyPoint))
    #add rubber bands to the new points
    snapGeometry = QgsGeometry.fromWkt(dumps(shplySnapPoint))
    r = QgsRubberBand(canvas,QGis.Point)
    r.setColor(Qt.red)
    print( r.x(),r.y())
    r.setToGeometry(snapGeometry,pointLayer)
