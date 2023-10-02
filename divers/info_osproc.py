# def __init__()
# node=svasekclusters().name_node()
# return node
try:
	import psutil
except:
	raise Exception

#try:#
#	import svasekclusters
#except:
#	raise Exception

def pids():
	return psutil.pids()
def names():
	names =[]
	for p in pids():
		names.append(naam(p))
	return names

def naam(pid):
	#naam=[];
	#for pnr in pids:
	#print psutil.Process(pid).name()
	naam=psutil.Process(pid).name()
	return naam
	
def	cpuperc(pid,deltaT=1):
	cpuperc=psutil.Process(pid).cpu_percent(interval=deltaT)
	return cpuperc

def	memperc(pid, deltaT=1):
	#for pnr in self.pids:
	#print psutil.Process(pnr).memory_percent(interval=deltaT)
	memperc=psutil.Process(pid).memory_percent()
	return memperc

def user(pid):
	user=psutil.Process(pid).username()
	return user
def status(pid):
	status= psutil.Process(pid).status()
	return status

class node_info:
    #try:
    import psutil 
    import socket
    #except Exception:
    #print("Error: %s" % Exception) #Exception.warning
    def cpu_count(self):
        x=self.psutil.cpu_count()
        return x
        #print x
    def cpu_percent(self,second=3):
        x=self.psutil.cpu_percent(second, percpu=True)
        return x
    def physmem_percent(self):
        x=self.psutil.virtual_memory().percent
        return x
    def name_node(self):
        temp=self.socket.gethostname()
        return temp		

class search():
	def __init__(self):
		#print 'start'
		self.pids=psutil.pids()
		#return pids
		#print 'stop'
	def pidbyname_literal(self,names):
		#return self.pids
		names=list(names)
		pnr=[]
		for n in iter(names):
			pnr.append([])
			for p in self.pids:
				#print n
				#print naam(p)
				if naam(p)==n:
					#pnr[-1].remove(None)
					pnr[-1].append(p)
		return pnr

	def pidbyname_regex(self,patroon):
		#https://docs.python.org/2/library/re.html
		#
		import re
		if isinstance(patroon,str):
			patroon=[patroon]
		pnr=[]
		for pat in patroon:	
			patobj=re.compile(pat)
			for p in self.pids:
					if patobj.search(naam(p))!=None:
						#pnr.append([])
						#print naam(p)
						#pnr[-1].remove(None)
						pnr.append(p)
		return pnr
		
	def pidbycpu(self,stat=None,N=None):
		import operator
		#top N
		pidcpu={}
		for p in self.pids:
			print(status(p))
			if status(p)==stat or stat==None:
				pidcpu[p]=cpuperc(p,deltaT=1)
		pidcpu_sorted=sorted(pidcpu.items(),key=operator.itemgetter(1),reverse=True)
		naamcpu={}
		return pidcpu_sorted
			
	def pidbyuser(self,usernaam='',stat=None):
		import operator
		#top N
		piduser={}
		for p in self.pids:
			try:
				print(status(p))
				if status(p)==stat or stat==None:
					piduser[p]=user(p)
			except NoSuchProcess:
				continue
		return piduser
			
		
		
		