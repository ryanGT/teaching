from matplotlib.transforms import BlendedGenericTransform
from matplotlib import patches
from matplotlib.patches import Circle, Arc
import matplotlib.pyplot as plt
plt.rcParams['mathtext.fontset'] = 'cm'
import numpy as np
dtr = np.pi/180

def transform_coords(coords, HT):
    if len(coords) == 2:
        coords = np.append(coords,[0,1])
    elif len(coords) == 3:
        coords = np.append(coords,[1])

    tcoords = np.dot(HT,coords)
    return tcoords


mygray = '#808B96'
grid_dict = {'linestyle':'dashed',\
             'color':mygray, \
             'linewidth':1.0, \
             'zorder':0, \
            }


class transformed_coords_sketch(object):
    """Throughout this class, frame A will be the global frame and
    frame B will be the rotated and/or translated frame."""
    def draw_rotated_line(self, start_coords, end_coords, HT, **plot_kwargs):
        start_A = transform_coords(start_coords, HT)
        stop_A = transform_coords(end_coords, HT)
        x_vect = [start_A[0],stop_A[0]]
        y_vect = [start_A[1],stop_A[1]]
        self.ax.plot(x_vect, y_vect, **plot_kwargs)


    def place_rotated_text(self, x, y, text, HT):
        rotated = transform_coords([x,y], HT)
        x_A = rotated[0]
        y_A = rotated[1]
        self.ax.text(x_A, y_A, text, va='center', \
                     fontdict=self.fontdict, ha='center')


    def place_text_A(self, x, y, text):
        self.place_rotated_text(x, y, text, self.eye)


    def place_text_B(self, x, y, text):
        self.place_rotated_text(x, y, text, self.HT)

            
    def draw_rotated_arrow(self, start_coords, end_coords, HT, \
                           fc='k', ec=None, lw=None, **plot_args):
        if ec is None:
            ec = fc
        start_A = transform_coords(start_coords, HT)
        stop_A = transform_coords(end_coords, HT)
        dx_A = stop_A[0]-start_A[0]
        dy_A = stop_A[1]-start_A[1]

        if lw is None:
            lw = self.arrow_lw

        self.ax.arrow(start_A[0], start_A[1], dx_A, dy_A, \
                      lw=lw, fc=fc, ec=ec, \
                      head_width=self.hw, head_length=self.hl, \
                      overhang = self.ohg, \
                      length_includes_head=True, clip_on = False, \
                      **plot_args)


    def draw_B_arrow(self, end_coords, start_coords=(0,0), \
                     fc='b', ec=None, zorder=1000, **plot_args):
        self.draw_rotated_arrow(start_coords, end_coords, HT=self.HT, \
                                ec=ec, fc=fc, zorder=zorder, **plot_args)
        
    def draw_A_arrow(self, end_coords, start_coords=(0,0), \
                     fc='b', ec=None, zorder=1000, **plot_args):
        self.draw_rotated_arrow(start_coords, end_coords, HT=self.eye, \
                                ec=ec, fc=fc, zorder=zorder, **plot_args)

    def draw_axis(self, HT, substr='A'):
        xlabel = self.x_label_pat % substr
        ylabel = self.y_label_pat % substr
        self.draw_rotated_arrow((self.xmin,0), (self.xmax,0), HT, \
                                fc=self.axis_color, lw=self.axis_lw)
        self.place_rotated_text(self.xmax+self.axis_label_shift, 0, xlabel, HT)
        self.draw_rotated_arrow((0,self.ymin), (0,self.ymax), HT, \
                                fc=self.axis_color, lw=self.axis_lw)
        self.place_rotated_text(0, self.ymax+self.axis_label_shift, ylabel, HT)


    def draw_axis_A(self):
        self.draw_axis(self.eye)


    def draw_axis_B(self):
        self.draw_axis(self.HT, substr='B')


    def draw_xticks(self, HT, ticks=None, dy=0.1, **plot_kwargs):
        kwargs = {'color':'k',\
                  'linewidth':2}
        kwargs.update(plot_kwargs)

        if ticks is None:
            ticks = np.arange(0, self.xmax, 1)

        
        for tick in ticks:
            start_tick = [tick, dy]
            end_tick = [tick, -dy]
            self.draw_rotated_line(start_tick, end_tick, HT, **kwargs)


    def draw_A_xticks(self, ticks=None, dy=0.1, **plot_kwargs):
        self.draw_xticks(self.eye,ticks=ticks, dy=dy, **plot_kwargs)


    def draw_B_xticks(self, ticks=None, dy=0.1, **plot_kwargs):
        self.draw_xticks(self.HT, ticks=ticks, dy=dy, **plot_kwargs)
        

    def draw_yticks(self, HT, ticks=None, dx=0.1, **plot_kwargs):
        kwargs = {'color':'k',\
                  'linewidth':2}
        kwargs.update(plot_kwargs)

        if ticks is None:
            ticks = np.arange(0, self.ymax, 1)

        for tick in ticks:
            start_tick = [-dx, tick]
            end_tick = [dx, tick]
            self.draw_rotated_line(start_tick, end_tick, HT, **kwargs)


    def draw_A_yticks(self, ticks=None, dx=0.1, **plot_kwargs):
        self.draw_yticks(self.eye,ticks=ticks, dx=dx, **plot_kwargs)


    def draw_B_yticks(self, ticks=None, dx=0.1, **plot_kwargs):
        self.draw_yticks(self.HT, ticks=ticks, dx=dx, **plot_kwargs)



    def draw_rotated_vertical_gridlines(self, HT, xlist=None, \
                                        ymin=0, ymax=None, plot_kwargs=None):
        if plot_kwargs is None:
            plot_kwargs = grid_dict

        if ymax is None:
            ymax = self.ymax

        if xlist is None:
            xlist = np.arange(0,self.xmax,1)

        for x in xlist:
            self.draw_rotated_line([x,ymin], [x,ymax], HT, **plot_kwargs)


    def draw_A_vertical_gridlines(self, xlist=None, **kwargs):
        self.draw_rotated_vertical_gridlines(self.eye, xlist=xlist,
                                             **kwargs)


    def draw_B_vertical_gridlines(self, xlist=None, **kwargs):
            self.draw_rotated_vertical_gridlines(self.HT, xlist=xlist,
                                                 **kwargs)


    def draw_rotated_horizontal_gridlines(self, HT, ylist=None, xmin=0, xmax=None, \
                                          plot_kwargs=None):
        if plot_kwargs is None:
            plot_kwargs = grid_dict

        if xmax is None:
            xmax = self.xmax

        if ylist is None:
            ylist = np.arange(0,self.ymax,1)
        

        for y in ylist:
            self.draw_rotated_line([xmin,y], [xmax,y], HT, **plot_kwargs)


    def draw_A_horizontal_gridlines(self, ylist=None, **kwargs):
        self.draw_rotated_horizontal_gridlines(self.eye, ylist=ylist,
                                               **kwargs)


    def draw_B_horizontal_gridlines(self, ylist=None, **kwargs):
        self.draw_rotated_horizontal_gridlines(self.HT, ylist=ylist,
                                               **kwargs)


    def draw_rotated_circle(self, x, y, r, HT, color='k', alpha=1, \
                            zorder=100):
        center_B = [x,y,0]
        center_A = transform_coords(center_B, HT)
        rot_circle = Circle((center_A[0], center_A[1]), r, \
                            color=color, alpha=alpha, \
                            zorder=zorder)
        self.ax.add_patch(rot_circle)


    def draw_circle_A(self, x, y, r, **kwargs):
        self.draw_rotated_circle(x, y, r, self.eye, **kwargs)
        

    def draw_circle_B(self, x, y, r, **kwargs):
        self.draw_rotated_circle(x, y, r, self.HT, **kwargs)


    def draw_circle_with_label(self, coords, HT, label='$P$', \
                               label_shift=(0.3,0.3), \
                               r=0.1, **kwargs):
        self.draw_rotated_circle(coords[0], coords[1], r, HT, **kwargs)
        labelx = coords[0]+label_shift[0]
        labely = coords[1]+label_shift[1]
        self.place_rotated_text(labelx, labely, label, HT)


    def set_arrow_lengths(self):
        self.hw = 1./30.*(self.ymax-self.ymin)
        self.hl = 1./20.*(self.xmax-self.xmin)
        self.lw = 2. # axis line width
        self.ohg = 0.3 # arrow overhang

        # compute matching arrowhead length and width
        #yhw = hw/(ymax-ymin)*(xmax-xmin)* height/width
        #yhl = hl/(xmax-xmin)*(ymax-ymin)* width/height

        
    def draw_circular_arc_A_coords(self, r, start_angle, stop_angle, \
                                   arrow_angle=85, delta_sign=-1, \
                                   head_length=0.4, head_width=0.2, \
                                   cw=False):
        """If the arc is drawn clockwise, cw=True.  This requires an arc with
        start_angle and stop_angle switched."""
        angle_rad = arrow_angle*dtr
        end_x = r*np.cos(stop_angle*dtr)
        end_y = r*np.sin(stop_angle*dtr)

        dx = (head_length) * np.cos(angle_rad)*delta_sign
        dy = (head_length) * np.sin(angle_rad)*delta_sign

        start_x = end_x - dx
        start_y = end_y - dy

        if cw:
            arc_start = stop_angle
            arc_end = start_angle
        else:
            arc_start = start_angle
            arc_end = stop_angle
            
        arc = Arc((0, 0),
                  r*2, r*2,  # ellipse width and height
                  theta1=arc_start, theta2=arc_end, linestyle='-', lw=2)
        self.ax.add_patch(arc)
        self.ax.arrow(start_x, start_y, dx, dy, \
                      head_width=head_width, head_length=head_length, \
                      fc='k', ec='k', length_includes_head=True)

        

    def axis_off(self):
        self.ax.set_axis_off()
        
        
    def __init__(self, HT, ax, \
                 xmax=5, xmin=-0.5, ymax=5, ymin=-0.5, \
                 xlims=[-3,7], ylims=[-3,7], \
                 fontdict = {'size': 18, 'family':'serif'}, \
                 xpat='$X_{%s}$', ypat='$Y_{%s}$', \
                 axis_label_shift=0.5, \
                 axis_color='k', axis_lw=2, \
                 arrow_lw=None, \
                 ):
                 self.HT = HT
                 self.eye = np.eye(4)
                 self.ax = ax
                 self.axis_label_shift = axis_label_shift
                 self.axis_color = axis_color
                 self.axis_lw = axis_lw
                 if arrow_lw is None:
                     arrow_lw=axis_lw
                 self.arrow_lw = arrow_lw
                 self.xmax = xmax
                 self.xmin = xmin
                 self.ymax = ymax
                 self.ymin = ymin
                 self.xlims = xlims
                 self.ylims = ylims
                 self.x_label_pat = xpat
                 self.y_label_pat = ypat
                 self.fontdict = fontdict
                 ax.set_xlim(self.xlims)
                 ax.set_ylim(self.ylims)
                 self.set_arrow_lengths()



class sketch_with_point_on_B(transformed_coords_sketch):
    def main(self, P_b, label='$P$', r=0.1, label_shift=(-0.3,0.3), \
             grid=False):
        self.draw_axis_A()
        self.draw_axis_B()
        self.axis_off()
        self.draw_B_xticks()
        self.draw_B_yticks()
        if grid:
            self.draw_B_vertical_gridlines()
            self.draw_B_horizontal_gridlines()
            
        self.draw_circle_B(P_b[0], P_b[1], r=r)
        labelx = P_b[0]+label_shift[0]
        labely = P_b[1]+label_shift[1]
        self.place_text_B(labelx, labely, label)


class sketch_without_point(transformed_coords_sketch):
    def main(self):
        self.draw_axis_A()
        self.draw_axis_B()
        self.axis_off()


        

class sketch_with_point_on_A(transformed_coords_sketch):
    def main(self, P_a, label='$P$', r=0.1, label_shift=(-0.3,0.3), \
             grid=False):
        self.draw_axis_A()
        self.draw_axis_B()
        self.axis_off()
        self.draw_A_xticks()
        self.draw_A_yticks()
        if grid:
            self.draw_A_vertical_gridlines()
            self.draw_A_horizontal_gridlines()

        self.draw_circle_A(P_a[0], P_a[1], r=r)
        labelx = P_a[0]+label_shift[0]
        labely = P_a[1]+label_shift[1]
        self.place_text_A(labelx, labely, label)




class sketch_Ry_with_point_on_B(transformed_coords_sketch):
    def __init__(self, *args, **kwargs):
        transformed_coords_sketch.__init__(self, *args, **kwargs)
        #self.x_label_pat = xpat
        self.y_label_pat = '$Z_%s$'
        

    def main(self, P_b, label='$P$', r=0.1, label_shift=(-0.3,0.3), \
             grid=False):
        self.draw_axis_A()
        self.draw_axis_B()
        self.axis_off()
        self.draw_B_xticks()
        self.draw_B_yticks()
        if grid:
            self.draw_B_vertical_gridlines()
            self.draw_B_horizontal_gridlines()
            
        self.draw_circle_B(P_b[0], P_b[1], r=r)
        labelx = P_b[0]+label_shift[0]
        labely = P_b[1]+label_shift[1]
        self.place_text_B(labelx, labely, label)
        


class sketch_Rx_with_point_on_B(transformed_coords_sketch):
    def __init__(self, *args, **kwargs):
        transformed_coords_sketch.__init__(self, *args, **kwargs)
        self.x_label_pat = '$Y_%s$'
        self.y_label_pat = '$Z_%s$'

    def main(self):
        self.draw_axis_A()
        self.draw_axis_B()
        self.axis_off()

        
class rotation_matrix_sketch(transformed_coords_sketch):
    def __init__(self,  HT, ax, \
                 xmax=1.5, xmin=0, ymax=1.5, ymin=0, \
                 xlims=[-1,2], ylims=[-1,2], \
                 axis_label_shift=0.2, \
                 **kwargs
                 ):
        transformed_coords_sketch.__init__(self, HT, ax, \
                                           xmax=xmax, xmin=xmin, \
                                           ymax=ymax, ymin=ymin, \
                                           xlims=xlims, ylims=ylims, \
                                           axis_label_shift=axis_label_shift, \
                                           axis_color='#818480', \
                                           axis_lw=2, \
                                           arrow_lw=3, \
                                           **kwargs)


    def main(self):
        self.draw_axis_A()
        self.draw_axis_B()
        self.axis_off()
