"""Vanaf operating systeem, via python, scripts of shell commando's starten uit operating systeem
Daarbij heb je de volgende keuzes	
	1) starten op een andere knoop
	2) wel of niet uitvoer naar het scherm wegschrijven. 
	3) invoerparamaters opgeven bij het script. 


Gebruik vanaf Bash command line:
Bijvoorbeeld, je wil 1)vanaf de bash command line, 2) het bashscript H_waqua.start-Simona_2014, 3) met de invoerparameter test opstarten 4) vanaf de knoop nerva, 5)zonder het wegschrijven van standard uitvoer naar het scherm 
	python -c "import startscript;print startscript.bashscript().shellscript('nerva','H_waqua.start-Simona_2014','test',False)"

Belangrijk, bashscript esh is noodzakelijk:  
	1) het zorgt ervoor dat je na ssh vanuit de home directory naar de huidige directory gaat. 
	2) bashprofile wordt ingeladen, na
"""




import os
import sys
from time import sleep
from subprocess import call,check_call

#print len(sys.argv)
#bashscript=sys.argv[1]
#print bashscript



class bashscript:
	#from subprocess import call, PIPE
	#import svasekfilepad
	
	"script starten in nieuwe shell: als je naar een andere knoop gaat "
	def shellscript(self,knoop,bashscript,inputpar='',output2screen=True):
		esh = '/home/bin/esh'

		#from svasekclusters import check
		import subprocess 

		#assert check().checknode(knoop),'Knoop klopt niet'
		assert type(inputpar) in (list,str),'Alleen string toegestaan voor inputpar'

		if isinstance(inputpar,list):
			bashinput=''
			for s in inputpar:
				bashinput=bashinput+ ' '+s
		elif isinstance(inputpar,str):
			bashinput= inputpar

 		#print [esh + ' '+ knoop+ ' '+bashscript+ ' ' +bashinput]
		#x=subprocess.Popen(esh+' '+knoop+' '+bashscript+' '+bashinput,shell=True)
		#x=subprocess.Popen(esh+' '+knoop+' '+bashscript+' '+bashinput,shell=True,stdout=subprocess.PIPE)
		#x=subprocess.Popen(esh+' '+knoop+' '+bashscript+' '+bashinput,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE )
		#x.wait()
		#x.communicate()[0]

		
		if output2screen:
			inputstring=esh+' '+knoop+' '+bashscript+' '+bashinput
			print(inputstring)
			x=subprocess.Popen(esh+' '+knoop+' '+bashscript+' '+bashinput,shell=True,stderr=subprocess.PIPE)
			print(' subprocess.Popen('+esh+' '+knoop+' '+bashscript+' '+bashinput+',shell=True,stderr=subprocess.PIPE)')
			while True: 
				out = x.stderr.read(1)
				if out=='' and x.poll() != None:
					break
				if out!='':
					sys.stdout.write(out)
					sys.stdout.flush()
		else:
			x=subprocess.Popen(esh+' '+knoop+' '+bashscript+' '+bashinput,shell=True,stdout=subprocess.PIPE)
			x.communicate()
			#fh=open('log.log','w')
			#x=subprocess.Popen(esh+' '+knoop+' '+bashscript+' '+bashinput,shell=True,stdout=fh)
				
			#print x.communicate()[0]
		print("einde shellscript")

	def script(self,bashscript,inputpar=''):
		#"script starten in huidige shell"
		
		assert type(inputpar) in (tuple,list,str),'Alleen list en string toegestaan voor inputpar'
		print(inputpar)
		#shell=False
		bashscript=bashscript+' '+inputpar
		print(bashscript)
		#if isinstance(inputpar,(list,str)):
		call(bashscript)
		#else:
		#raise TypeError('Alleen list en string toegestaan voor inputpar')

