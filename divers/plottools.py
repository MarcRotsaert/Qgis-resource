""" Verzameling functies om plotten van data te vergemakkelijken"""
import matplotlib.pyplot as plt
#from matplotlib.pyplot import xlim,ylim, quiverkey,cm
from info_waquaveld import veldstatistiek,roostereigenschappen#,afstandmatrix
import numpy as np
#import datetick as Datetick



class MroQuiver:
    def quiverscaling(self,X,Y,U,V=None):
        """ Bepaling van een redelijke waarde voor quiver schaal factor.
            Bedoeling is dat pijlen niet over andere punten heen komen, maar nog wel voldoende omvang hebben
            U,V = Veld stroomsnelheid in U en V richting, 
                OF 
            U = absolute stroomsnelheid 
            X,Y = veld met X en Y coordinaten
            Aannames:
                1) Voor quiver   "scaling_units = xy "
                2) axis equal 
            """
        if V is not None:
            vel=np.sqrt(U**2+V**2)
        else:
            vel=U
        if type(vel)==np.ma.MaskedArray:
            unmask=True
        else:
            unmask=False

        print('Bepaal schaalgrootte voor quiver pijl')
        #1)Bepaal 10% hoogste snelheid. 
        #Gemiddelde van 10% hoogste snelheden wordt de maatgevende snelheid. 

        velunmasked=veldstatistiek.overig(vel).veld2sortarray(unmask=unmask)
        
        print('gesorteerde stroomsnelheid')
        print(velunmasked)
        n=int(velunmasked.size*0.1) #10% grootste stroomsnelheden
        velmaatgevend=velunmasked[-n:].mean()
        print('maatgevende stroomsnelheid: '+str(velmaatgevend))

        #matr=afstandmatrix(X,Y)
        #print(matr.min())
        try:
            resol=roostereigenschappen(X,Y).resolution()
            resol=resol.flatten()
        except:
            return X,Y
        dxy= resol.mean()#dxy= resol.min(axis=1).mean()
        print('maatgevende afstand tussen roostercellen: '+ str(dxy))
        scale = float(velmaatgevend)/(float(dxy))
        print('Let op 1)Invoerparameter quiver   "scaling_units = xy ";\n2)gebruik plot_tools.axisequal()')
        return scale

    def quiverkey_current(self,Q): 
        """    Default quiverkey in figuur
        Q= handle naar quiver."""
        qk = plt.quiverkey(Q, 0.9, 0.95, 2, r'$2 \frac{m}{s}$',
                   labelpos='E',
                   coordinates='figure',
                   fontproperties={'weight': 'bold', 'size':20})  
        return qk

class MroLine:
    def lcolormap(self,zmin_or_array,zmax=np.nan,colmap=plt.cm.jet_r):
        import matplotlib.colors as colors
        if type(zmin_or_array)==np.ndarray:
            scalarMap=plt.cm.ScalarMappable()
            scalarMap.set_array(zmin_or_array)
            scalarMap.autoscale()
        elif type(zmin_or_array)==int:
            assert(zmax!=np.nan), "Geef ook max-waarde op"
            cNorm  = colors.Normalize(vmin=zmin, vmax=zmax)
            scalarMap = plt.cm.ScalarMappable(norm=cNorm, cmap=colmap)
        else:
            raise TypeError
        return scalarMap

    def legend_lcolormap(self,map,nrclass):
        cl=map.get_clim()
        interval=(cl[1]-cl[0])/nrclass
        valcol=[]
        for a in np.arange(cl[0],cl[1]+interval,interval):
            valcol.append({a:map.to_rgba(a)})
        return valcol


class MroAxis():
    def __init__(self,ax):
        import datetick
        #if isinstance(ax,plt.Axes)!=False:
        #    raise TypeError
        self.ax=ax
        #self.Datetickint=datetick.Tickint(ax)
        #self.Datetickform=datetick.Tickform(ax)
        #print(dir()#print dir(self))

    def axisequal(self,aslim=None):
        """ axis('equal') werkt niet naar behoren voor masked arrays. Vandaar dit alternatief'"""
        #soms werkt axis('equal') niet zo goed, bijvoorbeeld bij masked arrays, met nan-waarden. 
        self.ax.set_aspect('equal')
        if aslim!=None:
            assert(len(aslim)==4),'aslim moet xmin,ymax,ymin,ymax'
            plt.xlim([aslim[0], aslim[1]])
            plt.ylim([aslim[2], aslim[3]])

    @staticmethod  
    def autodetermineplotaxis(xdata,ydata):
        axlim=plt.gca().axis()
        #print(axlim)
        if axlim!=(0,1,0,1):
            #print('grrr')
            try:
                dx=np.abs(np.nanmin(xdata)-axlim[0])+np.abs(np.nanmax(xdata)-axlim[1])
                dy=np.abs(np.nanmin(ydata)-axlim[2])+np.abs(np.nanmax(ydata)-axlim[3])
            except:
                return xdata
            print(axlim)
            print(np.nanmax(xdata))
            print(np.nanmin(xdata))
            print(dx/(axlim[1]-axlim[0]))
            print(dy/(axlim[3]-axlim[2]))
            
            if dx/(axlim[1]-axlim[0])> 1.5 or dy/(axlim[3]-axlim[2])>1.5: 
                print('Data valt ruim buiten Actieve Assenstelsel')
                print('Plot data in nieuwe figuur')
                plt.figure() #maak figuur met nieuwe assen. 
                ax=plt.gca()
            else:
                ax=plt.gca()
        else:
            ax=plt.gca()
        return ax

class MroTick:
    def __init__(self,ax):
        import datetick
        self.ax=ax
        self.Datetickint=datetick.Tickint(ax)
        self.Datetickform=datetick.Tickform(ax)
        #print(dir()#print dir(self))
        
    def setFontsize(self,fs,xyaxis='xy'):
        for l in xyaxis:
            if 'x'==l:
                for ti in ax.xaxis.get_major_ticks():
                    ti.label.set_fontsize(fs)
            if 'y'==l:
                for ti in ax.yaxis.get_major_ticks():
                    ti.label.set_fontsize(fs)

    def removeOffset(self):
        """Verwijder offset uit as en geef volledige waarde weer op de as"""
        self.ax.ticklabel_format(useOffset=False)
        
class MroColormap:
    def return_GnYlBl(self,reverse=False):
        GnYlBu={u'blue': np.array([(0, 0.6450980484485626, 0.6450980484485626),
          (0.25, 1, 1 ),
          (0.5, 0., 0.),
          (.8, 0.4333333492279053, 0.4333333492279053),
          (1, 0.0333333492279053, 0.0333333492279053),
          ]),
         u'green': np.array([
          (0, 0.11372549086809158, 0.11372549086809158),
          (0.25, 0.6, 0.6),  
          (0.5, 1.0, 1.0),
          (0.8, 0.8039215803146362, 0.8039215803146362),
          (1, 0.4539215803146362, 0.4539215803146362),
          ]),
         u'red': np.array([(0, 0.0313725508749485, 0.0313725508749485),
          (0.25,0.6,0.6),  
          (0.5, 1.0, 1.0),
          (0.8, 0.29803921580314636, 0.29803921580314636),
          (1, 0.05803921580314636, 0.05803921580314636),
          ])}
                                                                                    
        if reverse==True:
            colormap={}
            for c in GnYlBu.keys():
                temp=np.zeros(GnYlBu[c].shape)
                temp[:,0]=GnYlBu[c][:,0]
                temp[:,1:]=np.flipud(GnYlBu[c][:,1:])
                colormap.update({c:temp})
        else:
            colormap=GnYlBu    
        
        plt.register_cmap(name='userdef_cm',data=colormap)
        cma0=plt.get_cmap('userdef_cm')
        return cma0,colormap
    
    def return_Norm(self,lim,nr_klasse):
        import matplotlib.colors as colors
        bounds=np.arange(lim[0],lim[1]+(lim[1]-lim[0])/float(nr_klasse-1),(lim[1]-lim[0])/float(nr_klasse-1))
        norm  = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
        return norm
    
    def set_Normpcolor(self,ax,lim,nr_klasse):
        import matplotlib.colors as colors
        import matplotlib.collections as collections
        ax_ch=ax.get_children()
        qm_inst=None
        
        for ch in ax_ch:
            if isinstance(ch,collections.QuadMesh):
                qm_inst=ch
                break
        
        bounds=np.arange(lim[0],lim[1]+(lim[1]-lim[0])/float(nr_klasse-1),(lim[1]-lim[0])/float(nr_klasse-1))
        
        norm  = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
        qm_inst.set_norm(norm)
        plt.clim(lim)
        #return norm
        """
        def return_norm_pcolor(lim,nr_klasse)
            import matplotlib.colors as colors
            bounds=np.arange(lim[0],lim[1]+(lim[1]-lim[0])/float(nr_klasse-1),(lim[1]-lim[0])/float(nr_klasse-1))
            #bounds = np.array([-11, -0.5,-0.25, -0.5, 0, 0.1,0.25,0.5, 11])
            norm  = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
            return norm
        """
        
        
        
###############################################################################
from matplotlib.patches import Polygon
#from matplotlib.mlab import dist_point_to_segment
from matplotlib import path
def default_vertices(ax):
    """Default to rectangle that has a quarter-width/height border."""
    xlims = ax.get_xlim()
    ylims = ax.get_ylim()
    w = np.diff(xlims)
    h = np.diff(ylims)
    x1, x2 = xlims + w // 4 * np.array([1, -1])
    y1, y2 = ylims + h // 4 * np.array([1, -1])
    return ((x1, y1), (x1, y2), (x2, y2), (x2, y1))


class MroMask:
    class MaskCreator(object):
        """An interactive polygon editor.
        Parameters
        ----------
        poly_xy : list of (float, float)
            List of (x, y) coordinates used as vertices of the polygon.
        max_ds : float
            Max pixel distance to count as a vertex hit.

        Key-bindings
        ------------
        't' : toggle vertex markers on and off.  When vertex markers are on,
              you can move them, delete them
        'd' : delete the vertex under point
        'i' : insert a vertex at point.  You must be within max_ds of the
              line connecting two existing vertices
        """
        def __init__(self, ax, poly_xy=None, max_ds=10):
            print(dir(self))
            self.showverts = True
            self.max_ds = max_ds
            if poly_xy is None:
                poly_xy = default_vertices(ax)
            color=[np.random.rand() for a in range(3)]
            self.poly = Polygon(poly_xy, animated=True,
                                fc=color, ec='none', alpha=0.4)
            #                    fc='y', ec='none', alpha=0.4)
            #self.poly = self.Polygon(poly_xy, animated=True,
            #                    fc='y', ec='none', alpha=0.4)
            ax.add_patch(self.poly)
            ax.set_clip_on(False)
            ax.set_title("Click and drag a point to move it; "
                         "'i' to insert; 'd' to delete.\n"
                         "Close figure when done.")
            self.ax = ax

            x, y = zip(*self.poly.xy)
            self.line = plt.Line2D(x, y, color='none', marker='o', mfc='r',
                                   alpha=0.2, animated=True)
            self._update_line()
            self.ax.add_line(self.line)

            self.poly.add_callback(self.poly_changed)
            self._ind = None # the active vert

            canvas = self.poly.figure.canvas
            canvas.mpl_connect('draw_event', self.draw_callback)
            canvas.mpl_connect('button_press_event', self.button_press_callback)
            canvas.mpl_connect('button_release_event', self.button_release_callback)
            canvas.mpl_connect('key_press_event', self.key_press_callback)
            canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
            self.canvas = canvas
        """
        def get_mask(self, shape):
            \"""Return image mask given by mask creator\"""
            h, w = shape
            y, x = np.mgrid[:h, :w]
            points = np.transpose((x.ravel(), y.ravel()))
            #mask = nxutils.points_inside_poly(points, self.verts)
            route=path.Path(self.verts)
            mask=route.contains_points(points)
            return mask.reshape(h, w)
        """
        def poly_changed(self, poly):
            'this method is called whenever the polygon object is called'
            # only copy the artist props to the line (except visibility)
            vis = self.line.get_visible()
            #Artist.update_from(self.line, poly)
            self.line.set_visible(vis)  # don't use the poly visibility state

        def draw_callback(self, event):
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
            self.ax.draw_artist(self.poly)
            self.ax.draw_artist(self.line)
            self.canvas.blit(self.ax.bbox)

        def button_press_callback(self, event):
            'whenever a mouse button is pressed'
            ignore = not self.showverts or event.inaxes is None or event.button != 1
            if ignore:
                return
            self._ind = self.get_ind_under_cursor(event)

        def button_release_callback(self, event):
            'whenever a mouse button is released'
            ignore = not self.showverts or event.button != 1
            if ignore:
                return
            self._ind = None

        def key_press_callback(self, event):
            'whenever a key is pressed'
            if not event.inaxes:
                return
            if event.key=='t':
                self.showverts = not self.showverts
                self.line.set_visible(self.showverts)
                if not self.showverts:
                    self._ind = None
            elif event.key=='d':
                ind = self.get_ind_under_cursor(event)
                if ind is None:
                    return
                if ind == 0 or ind == self.last_vert_ind:
                    print("Cannot delete root node")
                    return
                self.poly.xy = [tup for i,tup in enumerate(self.poly.xy)
                                    if i!=ind]
                self._update_line()
            elif event.key=='i':
                xys = self.poly.get_transform().transform(self.poly.xy)
                p = event.x, event.y # cursor coords
                for i in range(len(xys)-1):
                    s0 = xys[i]
                    s1 = xys[i+1]
                    d = dist_point_to_segment(p, s0, s1)
                    if d <= self.max_ds:
                        self.poly.xy = np.array(
                            list(self.poly.xy[:i+1]) +
                            [(event.xdata, event.ydata)] +
                            list(self.poly.xy[i+1:]))
                        self._update_line()
                        break
            elif event.key=='v':
                print(self.verts)
                return
            self.canvas.draw()

        def motion_notify_callback(self, event):
            'on mouse movement'
            ignore = (not self.showverts or event.inaxes is None or
                      event.button != 1 or self._ind is None)
            if ignore:
                return
            x,y = event.xdata, event.ydata

            if self._ind == 0 or self._ind == self.last_vert_ind:
                self.poly.xy[0] = x,y
                self.poly.xy[self.last_vert_ind] = x,y
            else:
                self.poly.xy[self._ind] = x,y
            self._update_line()

            self.canvas.restore_region(self.background)
            self.ax.draw_artist(self.poly)
            self.ax.draw_artist(self.line)
            self.canvas.blit(self.ax.bbox)

        def _update_line(self):
            # save verts because polygon gets deleted when figure is closed
            self.verts = self.poly.xy
            self.last_vert_ind = len(self.poly.xy) - 1
            self.line.set_data(zip(*self.poly.xy))

        def get_ind_under_cursor(self, event):
            'get the index of the vertex under cursor if within max_ds tolerance'
            # display coords
            xy = np.asarray(self.poly.xy)
            xyt = self.poly.get_transform().transform(xy)
            xt, yt = xyt[:, 0], xyt[:, 1]
            d = np.sqrt((xt - event.x)**2 + (yt - event.y)**2)
            indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
            ind = indseq[0]
            if d[ind] >= self.max_ds:
                ind = None
            return ind

        @classmethod
        def return_maskobject(self):
            return self

        def get_mask(self, x,y):
            """Return image mask given by mask creator"""
            #h, w = shape
            #y, x = np.mgrid[:h, :w]
            points = np.transpose((x.ravel(), y.ravel()))
            #mask = nxutils.points_inside_poly(points, self.verts)
            route=path.Path(self.verts)
            mask=route.contains_points(points)
            #return mask.reshape(h, w)
            return mask