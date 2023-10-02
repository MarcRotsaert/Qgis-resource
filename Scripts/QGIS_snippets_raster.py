#____________________________________________________________________________________________
#Rastercalculation 1
path_out = 'C:/temp'
raster_in =  r'D:\TEMP\Qgis\voorbeeldbestanden\overig\AHN_clipped_kv1_0.tif'

rl = QgsRasterLayer(raster_in)
qgsproject = QgsProject.instance()
qgsproject.addMapLayer(rl)
entries = []
# Define band1
boh1 = QgsRasterCalculatorEntry()
# boh1.ref = 'AHN_clipped_kv1_0@1'
boh1.ref = raster_in+'@1'
boh1.raster = rl
boh1.bandNumber = 1
entries.append( boh1 )
#calc = QgsRasterCalculator( 'AHN_clipped_kv1_0@1-0.26', 
kruinhoogte = 2
kv = 'a'
rasternr = 0 
wd = 'test'
calc = QgsRasterCalculator( raster_in+'@1-'+str(kruinhoogte), 
	os.path.join(path_out,'AHN_kruinhoogte_kv'+str(kv)+'_'+str(rasternr)+'_'+wd+'.tif'), 
	'GTiff',
	rl.extent(), 
	rl.width(), 
	rl.height(), 
	entries)
calc.processCalculation()

#____________________________________________________________________________________________
#Rastercalculation 2
import Layers as La

path_out = r'D:\TEMP\Qgis\voorbeeldbestanden\overig'
ahnlayers = ['M_09DZ1','M_14BN1', 'M_14BN2', 'M_14BZ1']

tinvp = 'tinpvp__teen20m'
la_tinvp = La.returnLayersbyname(tinvp)[0]
for ahnl in ahnlayers:
    la_ahn =  La.returnLayersbyname(ahnl)[0]
    print(la_ahn)
    boh1 = QgsRasterCalculatorEntry()
    #boh1.ref = 'AHN_clipped_kv1_0@1'
    boh1.ref = ahnl+'@1'
    boh1.raster = la_ahn
    boh1.bandNumber = 1
    entries=[]
    entries.append( boh1 )
    boh2 = QgsRasterCalculatorEntry()
    #boh1.ref = 'AHN_clipped_kv1_0@1'
    boh2.ref = tinvp+'@1'
    boh2.raster = la_tinvp
    boh2.bandNumber = 1
    entries.append( boh2 )
    
    calc = QgsRasterCalculator( ahnl+'@1 - '+ tinvp +'@1', 
        os.path.join(path_out,'vp20m_'+str(ahnl)+'.tif'), 
        'GTiff',
        la_ahn.extent(), 
        la_ahn.width(), 
        la_ahn.height(), 
        entries)
    calc.processCalculation()
    print(calc.lastError())
	