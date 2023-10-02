import numpy as np
class value:
	""" 
	Invoer: numpy-array
	Uitvoer: Waarde uit het veld  
	"""
	def __init__(self,Veld):
		self.Veld=Veld

	def max_value(self,):
		
		return np.nanmax(self.Veld)

	def min_value(self,):
		return np.nanmin(self.Veld)

	def mean_value(self,):
		return np.nanmean(self.Veld)

class index:
	"""
	Invoer: numpy-array
	Uitvoer: index nummer array  
	"""
	def __init__(self,Veld):
		from veldstatistiek import value
		self.Veld=Veld
		self.value=value
	def max_index(self,):
		"""index nummers voor maximale waarden"""
		maxval=self.value(self.Veld).max_value()
		#return np.ma.where(self.Veld==maxval)
		return np.array([np.ma.where(self.Veld==maxval)]).T.squeeze()

	def min_index(self,):
		"""index nummers voor minimale waarden"""
		minval=self.value(self.Veld).min_value()
		return np.array(np.ma.where(self.Veld==minval)).T.squeeze()

	def exceedance_index(self,value):
		"""index overschrijding waarde"""
		return np.array(np.ma.where(self.Veld>value)).T

	def deficit_index(self,value):
		"""index onderschrijding waarde"""
		return np.array(np.ma.where(self.Veld<value)).T

	def between_index(self,value1,value2):
		"""index tussen twee waarden"""
		val_under=np.min([value1,value2])
		val_upper=np.max([value1,value2])
		return np.array(np.ma.where((self.Veld>val_under) &(self.Veld<val_upper))).T

	def notbetween_index(self,value1,value2):
		"""index NIET tussen twee waarden"""
		val_under=np.min([value1,value2])
		val_upper=np.max([value1,value2])
		#print val_under
		#print np.where((self.Veld<val_under)|(self.Veld>val_upper))
		#print np.ma.where((self.Veld<val_under) &(self.Veld>val_upper))
		return np.array(np.ma.where((self.Veld<val_under) |(self.Veld>val_upper))).T



class overig:
	""" 
	Invoer: numpy-array
	Uitvoer: Divers  
	"""
	def __init__(self,Veld):
		self.Veld=Veld
	def nr_mask(self):
		"""Bepaal aantal gemaskerde waarden in een veld"""
		if np.ma.isMaskedArray(self.Veld):
			nmask=self.Veld.mask.sum()
		else:
			nmask=False
		return nmask
	def veld2sortarray(self,unmask=False):
		""" """
		if unmask==True:
			Array=self.Veld.compressed()
		else:
			Array= self.Veld.flatten()
		Array.sort()
		return Array

