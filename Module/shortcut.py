from qgis.core import QgsVectorLayer,QgsRasterLayer, QgsApplication,QgsGeometry
"""from qgis.gui import QgsLegendInterface"""
import VectorStyle
import RasterStyle
import VectorImportExport as VIE
import Layers
import os,numpy
from qgis.utils import iface
#from PyQt5.QtWidgets import * #from PyQt4.QtCore import *
#from PyQt5.QtWidgets import QFileDialog#from PyQt4.QtGui import QFileDialog
from PyQt5.QtWidgets import QFileDialog

def getFileDialogue(directory='Z:/',filter='',caption=u"Open File"):
	#fileName = QFileDialog.getOpenFileName(caption=u"Open File", directory='', filter=filter("netCDF Files (*.nc *.cdf *.nc2 *.nc4)"));
	fileName = QFileDialog.getOpenFileName(caption=caption, directory=directory, filter=filter);
	return fileName
	
def getDirectoryDialogue(directory='Z:/'):
	directory=QFileDialog.getExistingDirectory(directory=directory)
	return directory

def selectFilepad(filenaam,pad,filter):
	print(filter)
	print(pad)
	print(filenaam)
	if filenaam==None:
		if pad==None:
			pad='Z:/'
		fp=getFileDialogue(directory=pad,filter=filter)
		pad,filenaam=os.path.split(fp)
	else:#pad==None
		if pad==None:
			assert(os.path.isfile(filenaam)),'onbestaande file '+filenaam
			pad,filenaam=os.path.split(filenaam)
		else:
			file=os.path.join(pad,filenaam)
			assert(os.path.isfile(os.path.join(file))),'onbestaande file '+file
	return filenaam,pad

def reverseNodes(layer):
    """Omdraaien van een lijnstuk"""
    try:
        if layer.geometryType()>0:
            layer.startEditing()
        else:
            print('Je probeert functie toe te passen op een puntlaag ! Dat Mag Niet!')
            raise Exception
    except AttributeError:#, Argument:
        print("Omdraaien lijn niet mogelijk, geen (geldige vector-)laag geselecteerd?")

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


def processinglist():
    for alg in QgsApplication.processingRegistry().algorithms():
        print(alg.id(), "->", alg.displayName())

def processinghelp(package, functionname):
    import processing
    f=processing.algorithmHelp(package+':'+functionname)
        
    
"""     
def proclist():
    from qgis.core import QgsApplication
    for alg in QgsApplication.processingRegistry().algorithms():
        print(alg.id(), "->", alg.displayName())  
"""        

def caxis(minmax,field=None, colorinvert=False,laagselectie=None,colormap=None):
	assert type(minmax)==list, 'minmax opgeven als een list'

	if laagselectie==None:
		laagselectie=Layers.returnLayersselected()
	if isinstance(laagselectie,str):
		laag=Layers.returnLayersbyname(laagselectie)
	elif isinstance(laagselectie,QgsVectorLayer) or isinstance(laagselectie,QgsRasterLayer):
		laag=[laagselectie]
	elif type(laagselectie)==list:
		laag=laagselectie
	else:
		raise TypeError#, type(laagselectie)

	if colormap==None:
			print(colormap)
			print('yes')
			colormap='Spectral'

	for l in laag:
		if isinstance(l,QgsVectorLayer):
			#assert(field!=None), 'voeg fieldname toe als invoerparameter'
			if field==None:
				try:
					#selectieattribute= l.rendererV2().classAttribute()
					selectieattribute= l.renderer().classAttribute()
				except:
					AttributeError, 'voeg field toe als invoerparameter'
				#fields=iface.activeLayer().pendingFields()
				fields=iface.activeLayer().fields()
				#if fields.fieldNameIndex(selectieattribute)>-1:
				if fields.indexFromName(selectieattribute)>-1:
					field=selectieattribute
				else:
					raise AttributeError#, selectieattribute+": attribuut is niet aanwezig op laag "
			klassegrenzen=numpy.arange(minmax[0],minmax[1],(float(minmax[1]-minmax[0])/10))
			VectorStyle.VectorStyleColorramp(l).colorrampRanges(field,klassegrenzen,invertcr=colorinvert,colorrampname=colormap)
		elif isinstance(l,QgsRasterLayer):
			#if colormap==None:
			#	print colormap
			#	print 'yes'
			#	colormap='Spectral'
			if colorinvert==False:
				print('gggg')
				RasterStyle.RasterStyleColorramp(l).colorrampRanges([minmax[0],minmax[1]],invertcr=False,colorrampname=colormap)
			elif colorinvert==True:
				print('yyyy')
				RasterStyle.RasterStyleColorramp(l).colorrampRanges([minmax[0],minmax[1]],colorrampname=colormap,invertcr=True)

def setcol(klassegrenzen,field=None, colorinvert=False,laagselectie=None,colormap=None):
	assert type(klassegrenzen)==list, 'klassegrenzen opgeven als een list'

	if laagselectie==None:
		laag=Layers.returnLayersselected()
	if isinstance(laagselectie,str):
		laag=Layers.returnLayerbyname(laagselectie)
	elif isinstance(laagselectie,QgsVectorLayer):
		laag=[laagselectie]

	if colormap==None:
		print(colormap)
		print('yes')
		colormap='Spectral'
	for l in laag:
		if isinstance(l,QgsVectorLayer):
			if field==None:
				#selectieattribute= l.rendererV2().classAttribute()
				selectieattribute= l.renderer().classAttribute()
				#fields=iface.activeLayer().pendingFields()
			else:
				selectieattribute= field
			fields=iface.activeLayer().fields()
			#if fields.fieldNameIndex(selectieattribute)>-1:
			if fields.indexFromName(selectieattribute)>-1:
				field=selectieattribute
				#print(field)
			else:
				raise AttributeError#, selectieattribute+": attribuut is niet aanwezig op laag "
				#assert(field!=None), 'voeg fieldname toe als invoerparameter'
			VectorStyle.VectorStyleColorramp(l).colorrampRanges(field,klassegrenzen,invertcr=colorinvert,colorrampname=colormap)
		else:
			#RasterStyle.RasterStyleColorramp(l).colorrampRanges(klassegrenzen,invertcr=colorinvert,discrete=True,colorrampname=colormap)
			RasterStyle.RasterStyleColorramp(l).colorrampRanges(klassegrenzen,invertcr=colorinvert,discrete=True,colorrampname=colormap)
			#raise TypeError, '(nog)niet toepasbaar op een rasterlaag e.d.'

def colormap(colormapnaam,colorinvert=False,laagselectie=None):
	if laagselectie==None:
		laag=Layers.returnLayersselected()
	elif isinstance(laagselectie,str):
		laag=Layers.returnLayerbyname(laag)
	elif isinstance(laagselectie,QgsVectorLayer):
		laag=[laagselectie]
	else:
		raise Exception#, laagselectie
	for l in laag:
		if isinstance(l,QgsVectorLayer):
			VectorStyle.VectorStyleColorramp(l).setColorrampName(l.rendererV2(),colormapnaam,invertcr=colorinvert)
		elif isinstance(l,QgsRasterLayer):
			rs=RasterStyle.RasterStyleColorramp(l)
			print(dir(l.renderer()))
			cril=l.renderer().shader().rasterShaderFunction().colorRampItemList()
			minval=cril[0].value
			maxval=cril[-1].value
			RasterStyle.RasterStyleColorramp(l).colorrampRanges([minval,maxval],colormapnaam,invertcr=colorinvert)
	
def inlfinelmesh(filenaam=None,imp_exp=None,pad=None,epsg=0):
	assert(imp_exp!=None),"geef op of mesh impliciet of expliciet is  ( imp_exp=[\'imp\' | \'exp\'])"
	filenaam,pad=selectFilepad(filenaam,pad,'')
	#if filenaam==None:
	#	if pad==None:
	#		pad='Z:/'
	#	fp=getFileDialogue(directory=pad,filter='*.out Mesh01.mat')
	#	pad,filenaam=os.path.split(fp)
	#else:#pad==None
	#	if pad==None:
	#		assert(os.path.isfile(filenaam)),'onbestaande file '+filenaam
	#		pad,filenaam=os.path.split(filenaam)
	#	else:
	#		file=os.path.join(pad,filenaam)
	#		assert(os.path.isfile(os.path.join(file))),'onbestaande file '+file
	ext=os.path.splitext(filenaam)[1]
	if ext=='.out':
		meshtype='sepran'
	elif filenaam=='Mesh01.mat':
		meshtype='mesh01'
	else:
		print('vermoedelijk sepran, op hoop van zegen.....')
		meshtype='sepran'
	print(meshtype)
	VIE.ImportFinelpolygon(pad).importMesh(epsg,filenaam,imp_exp,meshtype)

def inlfinelascii(filenaam=None,imp_exp=None,pad=None,meshlaag=None):
	assert(imp_exp!=None),"geef op of mesh impliciet of expliciet is  ( imp_exp=[\'imp\' | \'exp\'])"
	import inl_finel as inlF
	filenaam,pad=selectFilepad(filenaam,pad,'')
	#if filenaam==None:
	#	if pad==None:
	#		pad='Z:/'
	#	fp=getFileDialogue(directory=pad,filter='')
	#	pad,filenaam=os.path.split(fp)
	#else:#pad==None
	#	assert(os.path.isfile(filenaam)),'onbestaande file '+filenaam
	#	pad,filenaam=os.path.split(filenaam)
	if imp_exp=='exp':
		if meshlaag==None:
			meshlaag=iface.activeLayer()
		VIE.ImportFinelpolygon(pad).appendAscii(filenaam,imp_exp,meshlayer=meshlaag)
	elif imp_exp=='imp':
		if type(meshlaag)==str:
			filenaammesh,padmesh=selectFilepad(meshlaag)
		elif meshlaag==None:
			fp=getFileDialogue(directory=pad,filter='*.1.out',caption="Open impliciet Sepran mesh ")
			padmesh,filenaammesh=os.path.split(fp)
		else:
			raise TypeError#,'impliciet moet je filenaam mesh opgeven of None' 
		mesh=inlF.Veld().mesh(padmesh,'sepran',impexp='imp',meshfile=filenaammesh)
		VIE.ImportFinelpolygon(pad).appendAscii(filenaam,imp_exp,meshlaag,mesh[1])
	paramnaam=filenaam[-3:]
	VectorStyle.VectorStyleColorramp(meshlaag).colorrampEqualinterval(paramnaam,10)


def inlfinelflow(pad=None,nr_of_file=None,meshlaag=None):
	if type(nr_of_file)==str:
		if pad==None:
			pad,filenaam=os.path.split(nr_of_file)
			nr=int(filenaam[4:9])
	elif type(nr_of_file)==int:
		pad=getDirectoryDialogue()
		assert(pad!=None), 'Indien je nummer van flow-file opgeeft, dan moet je pad als invoer opgeven'
		nr =nr_of_file
	else:
		filenaam,pad=selectFilepad(nr_of_file,pad,'Flow*.mat')
		#if pad==None:
		#	pad='Z:/'
		#	fp=getFileDialogue(directory=pad,filter='Flow*.mat')
		#	pad,filenaam=os.path.split(fp)
		#else:#pad==None
		#	assert(os.path.isfile(filenaam)),'onbestaande file '+filenaam
		#	pad,filenaam=os.path.split(filenaam)
		nr=int(filenaam[4:9])
	if meshlaag==None:
		meshlaag=iface.activeLayer()
	print(meshlaag)
	#dic=VIE.ImportFinelpolygon(pad).appendFlow(nr,meshlayer=meshlaag())
	#if True:
	VectorStyle.VectorStyleColorramp(meshlaag()).colorrampEqualinterval(str(nr)+'_H',10)
		#return dic


def inlrgf(filenaam=None,pad=None):
	filenaam,pad=selectFilepad(filenaam,pad,'')
	"""if filenaam==None:
		if pad==None:
			pad='Z:/'
		fp=getFileDialogue(directory=pad,)
		pad,filenaam=os.path.split(fp)
	else:#pad==None
		assert(os.path.isfile(filenaam)),'onbestaande file '+filenaam
		pad,filenaam=os.path.split(filenaam)
	"""
	VIE.ImportWaquapolygon().importRgf(0,filenaam,pad,toscreen=True)

	
def settransparency(value, layer=None):
	assert 0 <=value <=1
	if layer is None:
		layer =  iface.activeLayer()
	layer.renderer().setOpacity(1-value)
	layer.triggerRepaint()
	


	
	
