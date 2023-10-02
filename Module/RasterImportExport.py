""" Gereedschap om raster data te exporteren/importeren van/naar Qgis"""

#from qgis.core import *
from qgis.core import QgsRasterLayer,QgsRasterFileWriter,QgsCoordinateReferenceSystem,QgsRasterPipe,QgsRectangle
import os,sys
import numpy as np
from osgeo import osr,gdal
from PyQt5 import QtGui 



TEMPDIR_WIN_1='D:/temp'
TEMPDIR_WIN_2='C:/TEMP'
TEMPDIR_LINUX=os.path.expanduser("~")#Bijvoorbeeld '/home/svasekz/mro'
"""
class window(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		
	def window(self,tinput):
		#app = QtGui.QApplication()
		#w = QtGui.QDialog()
		b = QtGui.QLabel(self)
		b.setText("Hello World!")
		b.setText(tinput[-1])
		self.setGeometry(100,100,200,50)
		b.move(50,20)
		self.setWindowTitle("PyQt")
		self.show()
		self.exec_()
		return 'grrrr'
		#sys.exit(app.exec_())
"""

class list(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)

	def list(self,tinput):
		def Clicked(item):
			#self.item=item.data(0)
			self.item=item
			#QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())
		#app = QtGui.QApplication()
		#w = QtGui.QDialog()
		listWidget = QtGui.QListWidget(self)
		listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
		#Resize width and height
		listWidget.resize(300,120)
		for tin in tinput:
			listWidget.addItem(tin); 
		#listWidget.addItem(tinput.pop()); 
		listWidget.itemClicked.connect(Clicked)
		self.show()
		self.exec_()
		return listWidget
		#sys.exit(app.exec_())



class RasterImportExport:
	TEMPDIR_LINUX='/home/svasekz/mro/TEMP'
	TEMPDIR_WIN='D:\TEMP'
	NODATA=-32768
	#def __init__():
	#print( 'ggg')
	#from matplotlib import pyplot
	#self.Layer=layer
	#self.Dataset=dataset



	def getTempdir(self):
		""" TEMP-directory: helpfunctie om (tussen)resultaten op te slaan"""
		#from matplotlib import pyplot
		if os.name=='nt':
			if os.path.exists(TEMPDIR_WIN_1):
				self.TEMPDIR=TEMPDIR_WIN_1
			elif os.path.exists(TEMPDIR_WIN_2):
				self.TEMPDIR=TEMPDIR_WIN_2
			else:
				raise 'Inaccurate TEMPDIR'
		else:
			self.TEMPDIR=self.TEMPDIR_LINUX
		#print( self.TEMPDIR)
		return self.TEMPDIR

	def getTempfile(self,ext):
		ext=ext.strip('.')
		a=1
		while os.path.exists(os.path.join(self.TEMPDIR,'tmp'+str(a)+'.'+ext )):
			a=a+1
		tempfile=os.path.join(self.TEMPDIR,'tmp'+str(a)+'.'+ext )
		return tempfile

	def getFilename(self,file,pad,ext):
		ext=ext.strip('.')
		if file==None:
			file_name=self.getTempfile(ext)
		else:
			if pad==None:
				file_name=file+'.'+ext
			else:
				file_name=os.path.join(pad,file)+'.'+ext

			p,f=os.path.split(file_name)
			if os.path.exists(p)==False:
				raise Error
		return file_name

	def getCoorarray(self):
		#rastersize=(self.Layer.dataProvider().xSize(),self.Layer.dataProvider().ySize())
		#rect=self.Layer.extent()
		#rect_afmeting=[rect.xMinimum(),rect.yMinimum(),rect.xMaximum(),rect.yMaximum()]
		(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = self.Dataset.GetGeoTransform()
		
		bandarray = self.Dataset.GetRasterBand(1).ReadAsArray()
		if x_rotation==0 and y_rotation==0: #rect ==linker bovenhoek 
			coorx=np.arange(upper_left_x, upper_left_x+x_size*bandarray.shape[1],x_size)
			#coorx=np.arange(self.rect_afmeting[0],self.rect_afmeting[2] ,x_size)
			COORX=np.array([coorx[0:bandarray.shape[1]]]*bandarray.shape[0])
			#coory= np.arange(self.rect_afmeting[3],self.rect_afmeting[1] ,y_size)
			coory=np.arange(upper_left_y,upper_left_y+y_size*bandarray.shape[0], y_size)
			COORY=np.array([coory[0:bandarray.shape[0]]]*bandarray.shape[1]).T
			print( COORY.shape)
			print( COORX.shape)
		else:
			raise NotImplementedError('Ga nog uit van ongeroteerd raster. in de toekomst wel mogelijk/nodig?')
			# print( upper_left_x)
			# X=rect_afmeting[2]-rect_afmeting[0]
			# Y=rect_afmeting[3]-rect_afmeting[1]
			# if upper_left_x>rect_afmeting[0]:
				# lower_left_x= rect_afmeting[0]
				# x1= upper_left_x-rect_afmeting[0]
				# x2 =X-x1
				# lower_left_y= rect_afmeting[3]-Y*x2/x1
			# elif upper_left_x>rect_afmeting[0]:
				# y1= rect_afmeting[3]-upper_left_y
				# y2 =Y-y1
				# lower_left_y= rect_afmeting[1]
				# lower_left_x= rect_afmeting[1]

		coordict={}
		coordict['y']=COORY
		coordict['x']=COORX
		return coordict

	def transformCoor(self,epsg):
		""""Transformeren naar een ander coordinatenstelsel (via epsg nummer). 
		Uitgevoerd met bibliotheken OSGEO (dus andere wijze dan vector data) """ 
		source_wkt = self.Dataset.GetProjectionRef()
		source_srs = osr.SpatialReference()
		source_srs.ImportFromWkt(source_wkt)
		dest_srs = osr.SpatialReference()
		dest_srs.ImportFromEPSG(epsg)

		if dest_srs.IsProjected()==False:
			raise ValueError('epsg zonder bijbehorend referentievlak gevonden')
		if source_srs.ExportToWkt()==dest_srs.ExportToWkt():
			print( 'source CRS == dest CRS')
		else:
			reproj_file = gdal.AutoCreateWarpedVRT(self.Dataset, source_wkt, dest_srs.ExportToWkt())
			gdal.ReprojectImage(self.Dataset, reproj_file, source_wkt,  dest_srs.ExportToWkt())
			self.Dataset=reproj_file

	def uitsnede(self,xmin,xmax,ymin,ymax):
		rect=QgsRectangle()
		rect.setXMinimum(xmin)
		rect.setXMaximum(xmax)
		rect.setYMinimum(ymin)
		rect.setYMaximum(ymax)
		return rect
		
		
class ImportRaster(RasterImportExport):
	def __init__(self):
		from matlab import loadmat,loadmatsimple
		#self.Pad=pad
		self.loadmat=loadmat
		self.loadmatsimple=loadmatsimple
		if os.name=='nt':
			self.TEMPDIR=self.TEMPDIR_WIN
		else:
			self.TEMPDIR=self.TEMPDIR_LINUX
		#self.NODATA=-32768

	def writearcinfoascii(self,rasterarray,fileai,cellsize, xll,yll,NODATA=None):
		if NODATA==None:
			NODATA=self.NODATA
		nrows,ncols=rasterarray.shape
		file_name=self.getFilename(fileai.strip('.asc'),None,'asc')
		
		g=open(file_name,'w')
		g.write('ncols        '+str(ncols)+ '\n')
		g.write('nrows        '+str(nrows)+ '\n')
		g.write('xllcorner    '+str(xll)+ '\n')
		g.write('yllcorner    '+str(yll)+ '\n')
		g.write('cellsize     '+str(cellsize)+ '\n')
		g.write('NODATA_value  '+str(NODATA)+ '\n')
		for a in range(nrows):
			for b in range(ncols):
				g.write(str(rasterarray[a][b]) + ' ')
			g.write('\n')
		print( 'bestand: '+fileai+ ' gereed.')

	"""
	def loadmatsimple(self,filemat,mpad):
		raster=self.loadmat(os.path.join(mpad,filemat))
		for k in raster.keys():
			if not k.startswith('__'):
				x=k
		print( raster[x])

		#if nrows==1:
		#	raise 'Waarschijnlijk geen matfile met enkel een matrix als input'
		self.raster=raster[x]
		return raster[x]
	"""

	def importMat(self,matfile,mpad,Zvar,cellsize,xll,yll,epsg,xflip=False,yflip=False,):
		""" matrix importeren als een raster
		Zvar=naam Z-matrix in matfile
		xll=x-coor lower left corner
		yll=Y-coor lower left corner
		xflip= flip raster in x-richting
		yflip= flip raster in y-richting
		"""
		fill_value=99999.0
		
		from qgis.core import QgsMapLayerRegistry 
		rasterraw=self.loadmat(matfile,mpad)
		
		rastertemp=np.ma.masked_invalid(rasterraw[Zvar])
		rastertemp.set_fill_value(fill_value)
		rastertemp=rastertemp.filled()
		if xflip==True:
			rastertemp=np.flipud(rastertemp)
		if yflip==True:
			rastertemp=np.fliplr(rastertemp)
		rasterproc=rastertemp
		#tempfile=self.getTempfile('asc')
		tempfile=self.getFilename(None,None,'asc')
		print( tempfile)
		self.writearcinfoascii(rasterproc,tempfile,cellsize,xll,yll,fill_value)
		matlayer=QgsRasterLayer(tempfile,'temp')
		matlayer.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))
		#print( matlayer.dataProvider().xSize())
		QgsMapLayerRegistry.instance().addMapLayer(matlayer)

	def importNetcdfvakloding(self,nfile,npad,tijdselectie=None):
		print( 'Werkt wel, maar min of meer een demo!!')
		from qgis.core import QgsMapLayerRegistry 
		import imp#,os.path
		import datetime
		#sys.path.append(0,r'C:\Users\mro\Anaconda\lib\site-packages\scipy')
		#os.chdir(r'C:\Users\mro\Anaconda\lib\site-packages\scipy')
		#Onderstaande is noodzakelijk, maar niet bevredigend
		
		#import scipy.io.netcdf as inc
		#import NETCDF4 as inc
		
		assert(os.path.isfile(r'C:\Program Files\Anaconda2\Lib\site-packages\scipy\io\netcdf.py'))
		try:
			(path, name) = os.path.split(r'C:\Program Files\Anaconda2\Lib\site-packages\scipy\io\netcdf.py')
			(name, ext) = os.path.splitext(name)
			(file, filename, data) = imp.find_module(name, [path])
			print( file)
			print( filename)
			print( data)
			inc=imp.load_module(name, file, filename, data)
		except:
			inc=imp.load_package('io',r'C:\Program Files\Anaconda2\Lib\site-packages\scipy\io')
		
		print( 'nog iets doen aan laagkeuze!!!!')
		nc_f=inc.netcdf_file(os.path.join(npad,nfile))
		T=nc_f.variables['time'].data
		print( nc_f.variables['time'].units)
		print( 'aantal tijdstippen: '+str(len(T)))
		X=nc_f.variables['x'].data
		Y=nc_f.variables['y'].data
		z=nc_f.variables['z'].data
		Z=z.copy()
		if tijdselectie==None:
			tijdselectie =range(len(T))
			tinput=[]
			for tijdstip in tijdselectie:
				dt=datetime.datetime(1970,1,1)+datetime.timedelta(T[tijdstip])
				tinput.append(dt.strftime('%y-%m-%d'))
			g=list().list(tinput)
			tijdselectie=[]
			for i in g.selectedIndexes():
				tijdselectie.append(i.row())
		else:
			tijdselectie=[tijdselectie]
		for tijdstip in tijdselectie:
			Zmat=np.flipud(Z[tijdstip,:,:])
			#Xmat=np.array([X]*X.shape[0])
			#Ymat=np.array([Y]*Y.shape[0]).T
			print( Zmat.shape)
			#return Zmat
			if Zmat.max>1e36:
				Zmat[Zmat>1e36]=self.NODATA

			#return X,Y,z
			cellsizex=np.diff(X)
			cellsizey=np.diff(Y)
			#print( cellsizex,cellsizey)
			checkcellsx=set(cellsizex)
			checkcellsy=set(cellsizey)
			print( checkcellsy)
			print( checkcellsx)
			
			assert len(checkcellsx)==1 and len(checkcellsy)==1, "geen vaste cellgrootte"
			assert checkcellsx.pop()==checkcellsy.pop(), "afmetingen in x richting wijkt af van afmeting in y richting: "
			epsg=nc_f.variables['crs'].getValue()
			tempfile=self.getTempfile('asc')
			print( tempfile)
			
			#return Xmat,Ymat
			self.writearcinfoascii(Zmat,tempfile[0:-4],cellsizex[0],X[0],Y[0])
			dt=datetime.datetime(1970,1,1)+datetime.timedelta(T[tijdstip])
			#nclayer=QgsRasterLayer(tempfile+'.asc',nfile+'_'+ str(T[tijdstip]))
			nclayer=QgsRasterLayer(tempfile,nfile+'_d+'+ dt.strftime('%y-%m-%d'))
			nclayer.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))
			print( nclayer.dataProvider().xSize())
			QgsMapLayerRegistry.instance().addMapLayer(nclayer)
			#return nc_f

class ExportRaster(RasterImportExport):
	def __init__(self,laag):
		if os.name=='nt':
			self.TEMPDIR=self.TEMPDIR_WIN
		else:
			self.TEMPDIR=self.TEMPDIR_LINUX
		if isinstance(laag,str):
			#assert type(pad)==str,"
			self.Layer=QgsRasterLayer(laag,'temp')
		elif isinstance(laag,QgsRasterLayer):
			self.Layer=laag
		else:
			#print( laag)
			raise AttributeError(laag+' is geen Geldige invoer voor raster laag')
		try:
			#print( dir(self))
			assert(self.Layer.isValid()==True), 'Verkeerd bestandstype?Verkeerde filenaam?Verkeerde directory?'
		except NameError:
			print( 'Invoer moet filenaam(string )zijn, of raster laag (bijvoorbeeld iface.activeLayer() zijn ')
		bc=self.Layer.bandCount()
		provider = self.Layer.dataProvider()
		path= provider.dataSourceUri()
		self.Dataset=gdal.Open(path)
		rect=self.Layer.extent()
		self.Rect_afmeting=[rect.xMinimum(),rect.yMinimum(),rect.xMaximum(),rect.yMaximum()]

	def exportReprojectGT(self,epsg_nieuw,tfile=None,pad=None):
		""" exporteren van rasterlaag naar andere crs."""
		print( 'lllllllllllllllllll')
		import processing
		epsg_ori=self.Layer.crs().postgisSrid()
		gdal="gdalogr:warpreproject"
		epsg_o="EPSG:"+str(epsg_ori)
		epsg_n="EPSG:"+str(epsg_nieuw)
		nodata=self.NODATA
		target_res=0
		method=0
		outp_datatype=5 #5=float point
		compres=0
		jpeg_comp=100
		zlevel=1
		predictor=1
		tiled=False
		bigtiff=0
		tfw=False

		file_name=self.getFilename(tfile,pad,'tif')
		print( file_name)
		t=processing.runalg(gdal,self.Layer,epsg_o,epsg_n,nodata,target_res, method, outp_datatype, compres,jpeg_comp ,zlevel,predictor, tiled, bigtiff, tfw,'',file_name)
		#processing.runalg("gdalogr:warpreproject",self.Layer,"EPSG:"+str(epsg_ori),"EPSG:"+str(epsg_nieuw),-9999,0,0,'',5, os.path.join(pad,tfile))
		return t

	def exportUitsnedeGT(self,xmin,xmax,ymin,ymax,resolutie_x,resolutie_y,tfile=None,tpad=None):
		"""Maak uitsnede uit een rasterlaag en sla op als nieuw tif-file."""
		crs=self.Layer.crs()
		rect=self.uitsnede(xmin,xmax,ymin,ymax)
		xsize=(xmax-xmin)/resolutie_x
		ysize=(ymax-ymin)/resolutie_y
		gprovider = self.Layer.dataProvider()
		pipe = QgsRasterPipe()
		pipe.set(gprovider.clone())
		file_name=self.getFilename(tfile,tpad,'tif')
		
		#if tpad==None:
		#	file_name=self.getTempfile('tif')
		#else:
		#	file_name=os.path.join(tpad,tfile+'.tif')
		file_writer = QgsRasterFileWriter(file_name)
		file_writer.writeRaster(pipe,xsize,ysize, rect,crs) 
		print( file_name+': gereed')

	def exportGeotiff(self,tfile=None,tpad=None,*args):
		ext='tif'
		print( len(args))
		if len(args)==0:
			provider = self.Layer.dataProvider()
			rect=provider.extent()
			pipe = QgsRasterPipe()
			pipe.set(provider.clone())
			file_name=self.getFilename(tpad,tfile,ext)
			print( file_name)
			file_writer = QgsRasterFileWriter(file_name)
			file_writer.writeRaster(pipe,provider.xSize(),provider.ySize(), provider.extent(),provider.crs()) 
		elif len(args)==1: #Reproject
			epsg=args[0]
			self.exportReprojectGT(epsg,tfile,tpad)
		elif len(args)==6:
			xmin,xmax,ymin,ymax,resolutie_x,resolutie_y=args
			self.exportUitsnedeGT(xmin,xmax,ymin,ymax,resolutie_x,resolutie_y,tfile,tpad)
		else:
			raise Error

	def exportMat(self,mfile=None,mpad=None):
		"""Exporteren van rasterlaag naar een mat file."""
		from matlab import savemat
		#print( self.Dataset.GetProjection())
		band = self.Dataset.GetRasterBand(1)
		bandarray=band.ReadAsArray()
		bandarray=bandarray.astype('f8')
		banddict={};#banddict['raster']=bandarray

		val=self.getCoorarray()
		banddict['x']=val['x'];banddict['y']=val['y'];
		banddict={'x':val['x'],'y':val['y'] ,'raster':bandarray} 
		file_name=self.getFilename(mpad,mfile,'mat')
		#filepad=os.path.join(pad,mile)
		savemat({'raster':banddict},file_name)
