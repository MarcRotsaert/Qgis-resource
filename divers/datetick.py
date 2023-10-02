#Standaard  minuten.
#from matplotlib.pyplot import gca,Axes
import matplotlib.dates as mdates
#import scipy.io as matimp
import datetime
from matplotlib.pyplot import gca,Axes,get_fignums

def check_ax(ax=None):
    if ax is None:
        assert get_fignums!=[],'nog geen figuur aanwezig'
        ax=gca()
    else:
        assert isinstance(ax,Axes)==True,    'geen Axes-instance ingevoerd!' 
        assert ax.get_xbound()!=0, 'Nog geen as gedefinieerd?'
    return ax
    
class Tickint:
    def __init__(self,ax=[]):
        ax=check_ax(ax)
        self.ax=ax
        
    def Autotick(self):
        """tick automatisch instellen op basis van aslimiet.
        #uitvoer:     1) Aangepaste as. 
        #        2) Locator-object, waarmee de assen op een grafiek ingesteld kan worden. 
        #Zie documentatie over de datetime object 	
        """
        ts,te=self.ax.get_xlim()
        Tstart=datetime.datetime.fromordinal(int(ts))+datetime.timedelta(ts%1)
        Teind=datetime.datetime.fromordinal(int(te))+datetime.timedelta(te%1)
        dt = Teind-Tstart #dt=datetime.timedelta= class die tijdverschil aangeeft tussen tstart en tstop
        if dt.days<=1:
            print('datetick.py: lengte periode: '+str(dt.total_seconds()/(60*60))+' uren')
            if dt.total_seconds()<2400:
                tickloc=mdates.MinuteLocator(byminute=range(0,60,5))
            elif dt.total_seconds()<7200:
                tickloc=mdates.MinuteLocator(interval=1,byminute=range(0,60,10))
            elif dt.total_seconds()<14400:
                tickloc=mdates.HourLocator(interval=1)
            elif dt.total_seconds()<60000:
                tickloc=mdates.HourLocator(byhour=range(0,24,4))
            else:
                tickloc=mdates.HourLocator(byhour=range(0,24,6))
        else:
            print('datetick.py: lengte periode: '+str(dt.days)+' dagen')
            if dt.days <3:
                tickloc=mdates.HourLocator(byhour=range(0,24,12))
            elif dt.days<5: 
                tickloc=mdates.DayLocator(interval=1)
            elif dt.days<32:
                tickloc=mdates.WeekdayLocator(interval=1,byweekday=1)
            elif dt.days<180:
                tickloc=mdates.MonthLocator(interval=1)
            elif dt.days<365:
                tickloc=mdates.MonthLocator(interval=2)
            elif dt.days<900:
                tickloc=mdates.MonthLocator(interval=3)
            elif dt.days<1555:
                tickloc=mdates.Yearlocator(interval=1)
            else:
                tickloc=mdates.Yearlocator(interval=3)
        #self.ax.xaxis.set_major_locator(tickloc)
        return tickloc
        
    def set_autotick(self,majmin='major'):
        tickloc=self.Autotick()
        #print(tickloc)
        if majmin=='major': 
            self.ax.xaxis.set_major_locator(tickloc)
        elif majmin=='minor':
            self.ax.xaxis.set_minor_locator(tickloc)
        else:
            raise 'ValueError: majmin==major of minor'
            
    def Regulartick(self,timeunit,interv=1):
        defined_timeunit={
            'minuut':mdates.MINUTELY,
            'uur':mdates.HOURLY,
            'dag':mdates.DAILY,
            'monthly':mdates.MONTHLY,
            'yearly':mdates.YEARLY}
        assert timeunit in defined_timeunit,'kies uit volgende invoer: '+str(defined_timeunit.keys())
        #tick instellen met een dagelijkse uurlijkse, etc interval
        rule = mdates.rrulewrapper(defined_timeunit[timeunit],interval=interv)#, byminute=range(0,60,5))
        """
        if timeunit.lower()=='dag':
            rule = mdates.rrulewrapper(mdates.DAILY,interval=interv)#, byminute=range(0,60,5))
        if timeunit.lower()=='uur':
            rule = mdates.rrulewrapper(mdates.HOURLY,interval=interv)#, byminute=range(0,60,5))
        if timeunit.lower()=='minuut':
            rule = mdates.rrulewrapper(mdates.MINUTELY,interval=interv)#, byminute=range(0,60,5))
        if timeunit.lower()=='monthly':
            rule = mdates.rrulewrapper(mdates.MONTHLY,interval=interv)#, byminute=range(0,60,5))
        if timeunit.lower()=='yearly':
            rule = mdates.rrulewrapper(mdates.YEARLY,interval=interv)#, byminute=range(0,60,5))
        """
        tickloc=mdates.RRuleLocator(rule)
        return tickloc

    def set_regulartick(self,timeunit,interv=1,majmin='major'):
        
        tickloc=self.Regulartick(timeunit,interv)
        if majmin=='major': 
            self.ax.xaxis.set_major_locator(tickloc)
        elif majmin=='minor':
            self.ax.xaxis.set_minor_locator(tickloc)
        else:
            raise 'ValueError: majmin==major of minor'

    def Specialtick(self,Tstart,Tstop):
        #B) generische class
        rule = mdates.rrulewrapper(mdates.MINUTELY, byminute=range(0,60,5))
        tickloc=mdates.RRuleLocator(rule)
        #self.ax.xaxis.set_major_locator(tickloc)
        return tickloc
        

class Tickform():
    def __init__(self,ax=[]):
        ax=check_ax(ax)
        self.ax=ax
        self.defined_specialforms={
            1:'%d/%m/%y',
            2:'W%W %y',
            3:'%H:%M',
            4:'%d/%m/%y %H:%M',
            5:'%d/%m',
            6:'%y',
            }
    def Autoform(self):
        locator=self.ax.xaxis.get_major_locator()
        form=mdates.AutoDateFormatter(locator)
        return form

    def set_autoform(self):
        form=self.Autoform()
        self.ax.xaxis.set_major_formatter(form)
        print(self.ax.xaxis.get_major_ticks()[0].label.get_text())
        #return self.ax.xaxis.get_major_formatter()
        
    def Specialform(self,nr):
        errorstring='Invoer was: ' + str(nr)+'\nmogelijke invoer: '+str(self.defined_specialforms.keys())+'\ntick format bij invoer: '+str(self.defined_specialforms.items())
        #defined_specialforms.items()
        assert nr in self.defined_specialforms, errorstring #defined_specialforms.items()
        form=mdates.DateFormatter(self.defined_specialforms[nr])
        #print(self.defined_specialforms[nr])
        """
        if nr==1:
            form=mdates.DateFormatter('%d/%m/%y')
        elif nr==2:
            #Week nummer, jaar
            form=mdates.DateFormatter('W%W %y')
        elif nr==3:
            #UUR:Minuut
            form=mdates.DateFormatter('%H:%M')
        """
        return form    

    def set_specialform(self,nr):
        #print(nr)
        form=self.Specialform(nr)
        #print(form)
        self.ax.xaxis.set_major_formatter(form)