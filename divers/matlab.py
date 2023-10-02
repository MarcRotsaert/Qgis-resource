"""
Functies om matlab data om te zetten / in te lezen van/naar matlab 
dit is GEEN verzameling matlabfuncties
"""

from datetime import datetime, timedelta
import scipy.io as matimp
import os
import numpy as np
import pdb


def preprocess_datenum(matlab_datenum):
	"""preprocessing matlab-datenum naar een list"""
	#1 datenum variabele in een numpy array zetten
	if isinstance(matlab_datenum,float)==True:
		matlab_datenum=np.array([matlab_datenum])
	elif isinstance(matlab_datenum,list)==True:
		matlab_datenum=np.array(matlab_datenum)
	elif isinstance(matlab_datenum,np.ndarray)==True:
		matlab_datenum=matlab_datenum.squeeze()
	else:
		raise TypeError
	#2: numpy array  naar een list zetten
	i=np.where(matlab_datenum==0)
	if i[0].shape[0]==0:
		matlab_datenum.tolist()
	elif i[0].shape[0]==1 and i[0]==0:
		matlab_datenum.tolist()
		#print matlab_datenum
	else:
		#print 'yes'
		# Wat is hier de bedoeling
		timax=matlab_datenum.max()
		if i[0][0]==0:
			matlab_datenum[i[0][1:]]= timax
		else:
			matlab_datenum[i[0][0:]]= timax
		#print matlab_datenum
		matlab_datenum.tolist()
	return matlab_datenum

def datenum2datetime(matlab_datenum,roundtoseconds=True):
	"""omzetten van matlab-datenum(waarde/list/array) naar python-datetime, variabeletype"""
	#print "datenum2datetime"
	#'preprocess'
	matlab_datenum=preprocess_datenum(matlab_datenum)
	python_datetime=[]
	for ml_dn in matlab_datenum:
		#print ml_dn
		if int(ml_dn)!=0:
			#print 'yes'
			dat=datetime.fromordinal(int(ml_dn)) + timedelta(days=ml_dn%1) - timedelta(days = 366)
		else:
			#pdb.set_trace()
			dat=datetime.fromordinal(1)

		#afronding op de seconde
		if roundtoseconds==True:
			discard=timedelta(microseconds=dat.microsecond)
			if discard >= timedelta(microseconds=500000):
				dat=dat-discard+timedelta(seconds=1)
			else:
				dat=dat-discard
		#Toevoegen aan list
		python_datetime.append(dat)

	return python_datetime

def datetime2datenum(python_datetime):
	"""omzetten van python datetime naar matlab datenum matrizx"""
	pythontijd=python_datetime 
	if isinstance(pythontijd,datetime):
		matlabtijd= float(pythontijd.toordinal()+float(366))+float(pythontijd.hour)/24+float(pythontijd.minute)/1440+float(pythontijd.second)/86400
	else:
		matlabtijd=[]
		for pt in pythontijd:
			matlabtijd.append(float(pt.toordinal()+float(366))+float(pt.hour)/24+float(pt.minute)/1440+float(pt.second)/86400)
	return matlabtijd

def loadmat(file,pad=os.getcwd()):
	"""laden van een matfile"""
	fmat=os.path.join(pad,file)
	mat=matimp.loadmat(fmat)
	return mat

def savemat( matinvoer, file,pad=os.getcwd()):
	"""Simpel opslaan van een matfile"""	
	if isinstance(matinvoer,dict):
		#matimp.savemat(fmat,mat)
		mat={}
		for m in matinvoer:
			if isinstance(matinvoer[m],np.ma.MaskedArray):
				array=matinvoer[m].filled()
			else:
				array=matinvoer[m]
			mat.update({m:array})
	elif isinstance(matinvoer,np.ndarray):
		mat=matinvoer
		if isinstance(matinvoer,np.ma.MaskedArray):
			mat=array.filled()
	else:
		raise TypeError
	fmat=os.path.join(pad,file)
	matimp.savemat(fmat,{'temp':mat})

def loadmat_struct(file,pad=os.getcwd()):
	"""laden van een matfile"""
	fmat=os.path.join(pad,file)
	mat=matimp.loadmat(fmat,struct_as_record=False,squeeze_me=True)
	return mat

def loadmatsimple(filemat,mpad):
	mat=loadmat(os.path.join(mpad,filemat))
	for k in mat.keys():
		if not k.startswith('__'):
			x=k
	print(mat[x])

	#if nrows==1:
	#	raise 'Waarschijnlijk geen matfile met enkel een matrix als input'
	raster=mat[x]
	return raster


def return_matlabexe():
	""" Geinstalleerde matlab in environment """ 
	g=[]
	for path in os.environ["PATH"].split(";"):
		if os.path.isfile(os.path.join(path, "matlab.exe")):
			g.append(os.path.join(path, "matlab.exe"))
	return g
	#return None