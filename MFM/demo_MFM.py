import MaakFinelMesh as MFM
from qgis.utils import iface
def demo1():
	MFM.TriangleInvoerLijn('demo1','C:\TEMP').startTriangleinvoer()

def demo2():
	MFM.TriangleInvoerPunt('demo2','C:\TEMP').startTriangleinvoer()

def demo3():
	MFM.Mesh('demo3','C:\TEMP','trinp_lijn').integraalMesh('exp','Triangle_2_beta')

def demo4():
	MFM.TriangleInvoerLijn('demo4','C:\TEMP').makeTriangleinvoer(iface.activeLayer())

def demo5(**kwargs):
	print kwargs
	if kwargs=={}:
		MFM.Mesh('demo5','C:\TEMP','temp.shp').integraalMesh('exp','Triangle_2_beta',False)
	else:
		MFM.Mesh('demo5','C:\TEMP','temp.shp').integraalMesh('exp','Triangle_2_beta',False,**kwargs)

def demo6():
	MFM.TriangleInvoerPunt('demo6','C:\TEMP').makeTriangleinvoer('ECSMv7 Regions any')
	MFM.Mesh('demo6','C:\TEMP','temp.shp','ECSMv7 Regions any').integraalMesh('exp','Triangle_2_beta')
