import Fields as Fi
import Features as Fe
from qgis.core import QgsRasterLayer,QgsField, QgsProject, QgsVectorLayer, QgsRasterCalculatorEntry, QgsRasterCalculator
import processing 
from PyQt5.QtCore import QVariant
import os
def extent2polygon(layerslist): 
    assert(isinstance(layerslist, list))
    #layerslist = iface.layerTreeView().selectedLayers()
    for l in layerslist:
        assert(isinstance(l, QgsRasterLayer))
        #inp={ 'ABSOLUTE_PATH' : False, 'CRS_FIELD_NAME' : '', 'CRS_FORMAT' : 0, 'LAYERS' : ['//iv.local/projecten/IN/INFR180133 SO3-245 Toets regionale keringen/04 Producten/02 Berekening/Wilhelminakanaal/4.AHN/Bijgesneden/331.tif'], 'OUTPUT' : 'TEMPORARY_OUTPUT', 'PATH_FIELD_NAME' : 'location', 'PROJq_DIFFERENCE' : False, 'TARGET_CRS' : None }
        inp={ 'LAYERS' : layerslist, 'PATH_FIELD_NAME' : 'location', 'ABSOLUTE_PATH':False, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
        proc_result = processing.run('gdal:tileindex',inp)
        
    l = QgsVectorLayer(proc_result['OUTPUT'])#processing.run('gdal:tileindex', inp, output)
    l.startEditing()
            
    QgsField('name',QVariant.String,'',)
    Fi.addFields(l,[QgsField('name',QVariant.String,'')])
    i = Fi.indexFieldname(l,'name')
    QgsProject.instance().addMapLayers([l])
    x=0
    for feat in l.getFeatures():    
        feat.setAttribute('name',layerslist[x].name())
        l.updateFeature(feat)
        x=x+1
    l.commitChanges()

	
def rastercalculation_diff (la_1,la_2,outputfile):
    """
    Bereken verschil tussen twee raster lagen: laag_2-laag_1
    la_1 = rasterlayer object
    la_2 = rasterlayer object
    outputfile = string, path/filename(.tif)

    Output: 

    """
    if os.path.filext(outputfile)[1]!='.tif':
        outputfile = os.path.filext(outputfile)[0]+'tif'
	#raster_in =     'N:\_INFRA_WATERSYSTEMEN\Software\Python\Marc\voorbeeldbestanden\overig\AHN_clipped_kv1_0.tif'
	#rl = QgsRasterLayer(raster_in)
	#QgsProject().addMapLayer(raster_in)
	
    entries = []
    boh1 = QgsRasterCalculatorEntry()
    #boh1.ref = 'AHN_clipped_kv1_0@1'
    la1_name = la_1.name()
    boh1.ref = la1_name+'@1'
    boh1.raster = la_1
    boh1.bandNumber = 1
    entries=[]
    entries.append( boh1 )
    boh2 = QgsRasterCalculatorEntry()
    #boh1.ref = 'AHN_clipped_kv1_0@1'
    la2_name = la_1.name()
    boh2.ref = la2_name+'@1'
    boh2.raster = la_2
    boh2.bandNumber = 1
    entries.append( boh2 )
	
    #calc = QgsRasterCalculator( ahnl+'@1 - '+ tinvp +'@1', 
    #    os.path.join(path_out,'vp20m_'+str(ahnl)+'.tif'), 
    calc = QgsRasterCalculator( la2_name+'@1 - ' + la1_name+'@1 - ' +'@1', 
        os.path.join(outputfile), 
        'GTiff',
        la_2.extent(), 
        la_2.width(), 
        la_2.height(), 
        entries)
    calc.processCalculation()
    print(calc.lastError())
    print(outputfile + ' created?')

