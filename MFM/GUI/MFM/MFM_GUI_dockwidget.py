# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MFMDockWidget
                                 A QGIS plugin
 1e MFM
                             -------------------
        begin                : 2016-11-18
        git sha              : $Format:%H$
        copyright            : (C) 2016 by mro
        email                : rotsaert@svasek.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.utils import iface
from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal

import MaakFinelMesh as MFM
import Layers

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MFM_GUI_dockwidget_0.4.ui'))

def resolve(basepath=None):
	if not basepath:
		basepath = os.path.dirname(os.path.realpath(__file__))
	#return os.path.join(basepath, name)
	return basepath
MFM.readMFMconffile=os.path.join(resolve(),'default_MFM.conf')


def checkInputlayers():
	""" 
	retourneer uit de legenda,lijnen en eventueel punten laag, die als triangle invoer laag kan dienen.
	Er wordt op 2 manieren geselecteerd: 
	1) geselecteerde lagen in de legenda
	indien geen geselecteerde lagen  beschikbaar 
	2) Actieve laag. Dit is de laatste laag die ingeladen is. 
	"""
	sellayers=iface.legendInterface().selectedLayers()
	if sellayers==[]:
		[unclassifiedlayers]=iface.activeLayer()
	else:
		unclassifiedlayers=sellayers
	pointmfmlayer=[]
	lijnmfmlayer=[]
	for l in unclassifiedlayers:
		layertype=Layers.returnVectorLayerGeometryType(l)
		if layertype=='Point':
			pointmfmlayer.append(l)
		elif layertype=='LineString':
			lijnmfmlayer.append(l)
	return pointmfmlayer,lijnmfmlayer

class MFMDockWidget(QtGui.QDockWidget, FORM_CLASS):

	closingPlugin = pyqtSignal()

	def __init__(self, parent=None):
		"""Constructor."""
		super(MFMDockWidget, self).__init__(parent)
		# Set up the user interface from Designer.
		# After setupUI you can access any designer object by doing
		# self.<objectname>, and you can use autoconnect slots - see
		# http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
		# #widgets-and-dialogs-with-auto-connect
		self.setupUi(self)

		self.actions = []
		self.pluginIsActive = True
		#self.dockwidget = None
		pb=self.pushButton_StartTI
		pb.clicked.connect(self.activateStartTI)
		pb_2=self.pushButton_MaakMesh
		pb_2.clicked.connect(self.activateMaakMesh)
		pb_3=self.pushButton_MaakTI
		pb_3.clicked.connect(self.activateMaakTI)

		self.initGui()
		self.Triangle.toggled.connect(self.toggleTriangleVersion)
		self.Triangle_2_beta.toggled.connect(self.toggleTriangleVersion)
		self.Triangle_3_beta.toggled.connect(self.toggleTriangleVersion)


	def initGui(self):
		print 'BLLBLBLBLLBLLBLBLBLBLBLB'
		import pathfilesvasek
		defaultWorkingdir=pathfilesvasek.Temp().getTempdir()#'D:/TEMP'
		defaultProjectname='defaultProj'
		self.Workingdir.setText(defaultWorkingdir)
		self.Projectname.setText(defaultProjectname)
		self.buildOptionalInput()
		self.toggleTriangleVersion()
		
		#if not basepath:
		#	basepath = os.path.dirname(os.path.realpath(__file__))
		#return os.path.join(basepath, name)

	def closeEvent(self, event):
		self.closingPlugin.emit()
		event.accept()

	def activateStartTI(self):
		Projectname=self.Projectname.text()
		Workingdir=self.Workingdir.text()
		
		MFM.TriangleInvoerLijn(Projectname,Workingdir).startTriangleinvoer()
		MFM.TriangleInvoerPunt(Projectname,Workingdir).startTriangleinvoer()

	def activateMaakTI(self):
		Projectname=self.Projectname.text()
		Workingdir=self.Workingdir.text()
		players,llayers=checkInputlayers()
		#sellayers=iface.legendInterface().selectedLayers()
		#if sellayers==[]:
		#	[mfmlayers]=iface.activeLayer()
		#else:
		#	mfmlayers=sellayers

		for p in players:
			MFM.TriangleInvoerPunt(Projectname,Workingdir).makeTriangleinvoer(p)
		for l in llayers:
			MFM.TriangleInvoerLijn(Projectname,Workingdir).makeTriangleinvoer(l)

	def activateMaakMesh(self):
		Projectname=self.Projectname.text()
		Workingdir=self.Workingdir.text()
		
		radiobuttons1=self.Triangle_version.findChildren(QtGui.QRadioButton)
		for r in radiobuttons1:
			if r.isChecked():
				Trianglename=r.text()
				#print Trianglename

		radiobuttons2=self.Expimp.findChildren(QtGui.QRadioButton)
		for r in radiobuttons2:
			if r.isChecked():
				Expimp=r.text()
				#print Expimp

		players,llayers=checkInputlayers()
		#print dir(self.inputtest.parent().windowTitle)
		#print self.inputtest.parent().objectName()
		#print self.inputtest.objectName()
		kwargs={}
		o=self.qtoolswgs84
		if o.isChecked():
			wgs84switch=True
			#kwargs.update({'wgs84':True})
		else:
			wgs84switch=False
			#kwargs.update({'wgs84':False})
		print kwargs
		
		varargoptions=self.qtoolsversions[Trianglename]['vararg']
		print varargoptions
		for o in varargoptions:
			if isinstance(o,QtGui.QCheckBox):
				variable=o.text()
				kwargs.update({variable:int(o.isChecked())})
			elif isinstance(o,QtGui.QLineEdit):
				try:
					variable=o.objectName()
					val=float(o.text())
					kwargs.update({variable:val})
				except: 
					pass
		#print kwargs

		args=None
		argoptions=self.qtoolsversions[Trianglename]['arg']
		print argoptions
		if argoptions!=[]:
			o=argoptions[0]
			try:
				val=float(o.text())
				args=[val]
			except: 
				pass
		#print dir(self.optionalInput)
		#print 'yeah'
		#return
		if players==[]: 
			print Projectname
			print Workingdir
			print kwargs
			print args
			print wgs84switch
			#return
			m=MFM.Mesh(Projectname,Workingdir,llayers[0])
		else:
			m=MFM.Mesh(Projectname,Workingdir,llayers[0],players[0])
		if args==None:
			#MFM.Mesh(Projectname,Workingdir,llayers[0]).integraalMesh(Expimp,Trianglename,wgs84=wgs84switch,**kwargs)
			args=()
			m.integraalMesh(Expimp,Trianglename,wgs84=wgs84switch,*args,**kwargs)
		else:
			m.integraalMesh(Expimp,Trianglename,wgs84switch,*args,**kwargs)
		"""
		#else:
		#	MFM.Mesh(Projectname,Workingdir,llayers[0]).integraalMesh(Expimp,Trianglename,wgs84switch,*args,**kwargs)
		
		#return
		#else:
		#	if args==None:
		#		MFM.Mesh(Projectname,Workingdir,llayers[0],players[0]).integraalMesh(Expimp,Trianglename,**kwargs)
		#	else:
		#		MFM.Mesh(Projectname,Workingdir,llayers[0],players[0]).integraalMesh(Expimp,Trianglename,*args,**kwargs)
		#MFM.Mesh(Projectname,Workingdir,iface.activeLayer()).integraalMesh('exp','Triangle_2_beta')
		#MFM.Mesh(Projectname,Workingdir,iface.activeLayer()).integraalMesh('exp',Trianglename)
		"""
	def toggleTriangleVersion(self):
		print self.qtoolsversions
		
		ch=self.optionalInput.findChildren(QtGui.QRadioButton)
		radiobuttons1=self.Triangle_version.findChildren(QtGui.QRadioButton)
		for r in radiobuttons1:
			qcb=r.findChildren(QtGui.QCheckBox)
			qle=r.findChildren(QtGui.QLineEdit)
			print qcb
			print qle
			Trianglename=r.text()#r_connect =r
			qtools=self.qtoolsversions[Trianglename]
			qtoolsvararg=qtools['vararg']
			qtoolsarg=qtools['arg']
			if r.isChecked():
				#switch=True
				print qtools
				for qt in qtoolsvararg:
					qt.setVisible(True)  #qt.setEnabled(True)
				#qtoolsarg=qtools['arg']
				for qt in qtoolsarg:
					qt.setVisible(True)
			else:
				switch=False
				for qt in qtoolsvararg:
					qt.setVisible(False)  #qt.setEnabled(True)
				#qtoolsarg=qtools['arg']
				for qt in qtoolsarg:
					qt.setVisible(False)

			#for c in qcb:
			#	c.setEnabled(switch)
			#for c in qle:
			#	c.setEnabled(switch)

	def buildOptionalInput(self):

		qtoolsversions={}
		Workingdir=self.Workingdir.text()
		Projectname=self.Projectname.text()
		ch=self.optionalInput.findChildren(QtGui.QRadioButton)
		radiobuttons1=self.Triangle_version.findChildren(QtGui.QRadioButton)
		
		for r in radiobuttons1:
			Trianglename=r.text()
			
			
			
			vararg=MFM.MakeTriangleGrid(1,'D:/',None,Trianglename).getarginMtg()['varargin']
			print vararg
			#options.update(vararg)
			qtools=[];qtoolsvararg=[];qtoolsarg=[]
			
			
			
			for o in vararg.keys():
				datatype=vararg[o]
				if datatype==bool:
					qtoolvararg=QtGui.QCheckBox()
				elif datatype==float:
					qtoolvararg=QtGui.QLineEdit()
					qtoolvararg.setValidator(QtGui.QDoubleValidator(0, 1E10,10) )
				print 'no'
				qtoolvararg.setParent(r)
				qtoolvararg.setObjectName(o)
				qtoolvararg.setText(o)
				#qtoolvararg.setDisabled(True)
				self.optionalInput.addWidget(qtoolvararg)
				qtoolsvararg.append(qtoolvararg)
			arg=MFM.MakeTriangleGrid(1,'D:/',None,Trianglename).getarginMtg()['arg']
			if arg!=[]:
				#Vooralsnog alleen voor Triangle, niet voor Triangle_2_beta en Triangle_3_beta
				qtoolarg=QtGui.QLineEdit()
				qtoolarg.setValidator(QtGui.QDoubleValidator(0, 1E10,10) )
				self.optionalInput.addWidget(qtoolarg)
				qtoolsarg.append(qtoolarg)
				#vararg.update({'maxarea':arg})
			
			#wgs84.update({'wgs84':bool}) #standaard erbij

			qtoolsversions.update({Trianglename:{'vararg':qtoolsvararg,'arg':qtoolsarg}})
		self.qtoolsversions=qtoolsversions
		
		qtoolwgs84=QtGui.QCheckBox()
		qtoolwgs84.setObjectName('wgs84')
		qtoolwgs84.setText('wgs84')
		self.optionalInput.addWidget(qtoolwgs84)
		self.qtoolswgs84=qtoolwgs84
		#print qtool.parent().objectName()
		#spacer = QtGui.QSpacerItem(0,
		#							0,
		#							QtGui.QSizePolicy.Expanding,
		#							QtGui.QSizePolicy.Maximum)
		#self.optionalInput.addItem(spacer)
			#self.optionalInput.setMargin(0)
			#self.inputtest=inputtest
				
			
			
			
			
			
