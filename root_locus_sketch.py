from matplotlib.transforms import BlendedGenericTransform
from matplotlib import patches
from matplotlib.patches import Circle, Arc
import matplotlib.pyplot as plt
plt.rcParams['mathtext.fontset'] = 'cm'
import numpy as np
dtr = np.pi/180

import control


mygray = '#808B96'
grid_dict = {'linestyle':'dashed',\
             'color':mygray, \
             'linewidth':1.0, \
             'zorder':0, \
}

class root_locus_sketch(object):
    def __init__(self, ax, \
                 xmax=2, xmin=-5, ymax=5, ymin=-5, \
                 xlims=[-3,7], ylims=[-3,7], \
                 fontdict = {'size': 20, 'family':'serif'}, \
                 axis_lw=2, \
                 ):
        self.ax = ax
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.axis_lw = axis_lw
        self.fontdict = fontdict
        
        

    def draw_arrow(self, start_coords, end_coords, \
                   fc='k', ec=None, lw=None, **plot_args):
        if ec is None:
            ec = fc
        # if lw is None:
        #     lw = self.arrow_lw
        ##start_A = transform_coords(start_coords, HT)
        ##stop_A = transform_coords(end_coords, HT)
        dx = end_coords[0]-start_coords[0]
        dy = end_coords[1]-start_coords[1]

        self.ax.arrow(start_coords[0], start_coords[1], dx, dy, \
                      lw=lw, fc=fc, ec=ec, \
                      width=0.01, \
                      head_width=self.hw, head_length=self.hl, \
                      #overhang = self.ohg, \
                      length_includes_head=True, clip_on = False, \
                      **plot_args)

        
    def draw_axis(self):
        self.draw_arrow((0,0), (self.xmax,0), \
                        lw=self.axis_lw)
                        #fc=self.axis_color, 
        #self.place_rotated_text(self.xmax+self.axis_label_shift, 0, xlabel, HT)
        self.draw_arrow((0,0), (0,self.ymax), \
                        lw=self.axis_lw)
        self.draw_arrow((0,0), (0,self.ymin), \
                        lw=self.axis_lw)
                        #fc=self.axis_color, 
        #self.place_rotated_text(0, self.ymax+self.axis_label_shift, ylabel, HT)
        self.draw_arrow((0,0), (self.xmin,0), \
                        lw=self.axis_lw)



    def set_arrow_lengths(self):
        self.hw = 1./30.*(self.ymax-self.ymin)
        self.hl = 1./20.*(self.xmax-self.xmin)
        self.lw = 2. # axis line width
        self.ohg = 0.3 # arrow overhang

        
    def axis_off(self):
        self.ax.set_axis_off()


    def draw_marker(self, point, style='go', size=12):
        self.ax.plot([np.real(point)],[np.imag(point)], \
                     style, markersize=size)


    def add_text(self, point, text, xoffset=0, yoffset=0, \
                 fontdict=None):
        if fontdict is None:
            fontdict = self.fontdict
        self.ax.text(np.real(point)+xoffset, np.imag(point)+yoffset, \
                     text, fontdict=fontdict)


    def draw_point_with_label(self, point, text, style='go', size=12, \
                          xoffset=0, yoffset=0, \
                          fontdict=None):
        self.draw_marker(point, style=style, size=size)
        self.add_text(point, text, xoffset=xoffset, yoffset=yoffset, \
                      fontdict=fontdict)


    def draw_line(self, start, end, linestyle='k--', **plot_kwargs):
        self.ax.plot([np.real(start), np.real(end)], \
                     [np.imag(start), np.imag(end)], \
                     linestyle)


    def draw_lines_to_point(self, point, pole_or_zero_list, \
                            linestyle='k--', **plot_kwargs):
        for pz in pole_or_zero_list:
            self.draw_line(pz, point, linestyle=linestyle, **plot_kwargs)
            

    def draw_poles(self, pole_list, style='rX', size=12):
        for i, p in enumerate(pole_list):
            j = i+1
            self.ax.plot([np.real(p)],[np.imag(p)], \
                         style, markersize=size)


    def plot_branches(self, rmat, **plot_kwargs):
        self.ax.plot(np.real(rmat), np.imag(rmat), **plot_kwargs)


    def label_axes(self, real_point=None, imag_point=None, fontdict=None):
        if real_point is None:
            real_point = self.xmax-0.7j
        if imag_point is None:
            imag_point = 0.3+self.ymax*1j
        self.add_text(real_point, 'Re', fontdict=fontdict)
        self.add_text(imag_point, 'Im', fontdict=fontdict)
        

    def label_points(self, points, labels, offsets=None, fontdict=None):
        N = len(points)
        if offsets is None:
            offsets = [(0,0)]*N
        elif len(offsets) == 1:
            offsets = N*offsets

        for p, label, offset in zip(points, labels, offsets):
            self.add_text(p, label, xoffset=offset[0], yoffset=offset[1], \
                          fontdict=fontdict)
            

    def draw_vertical_gridlines(self, xlist=None, \
                                ymin=None, ymax=None, plot_kwargs=None):
        if plot_kwargs is None:
            plot_kwargs = grid_dict

        if ymax is None:
            ymax = self.ymax

        if ymin is None:
            ymin = self.ymin

        if xlist is None:
            xlist = np.arange(0,self.xmax,1)

        for x in xlist:
            self.ax.plot([x,x], [ymin,ymax], **plot_kwargs)


    def draw_horizontal_gridlines(self, ylist=None, \
                                xmin=None, xmax=None, plot_kwargs=None):
        if plot_kwargs is None:
            plot_kwargs = grid_dict

        if xmax is None:
            xmax = self.xmax

        if xmin is None:
            xmin = self.xmin

        if ylist is None:
            ylist = np.arange(self.ymin,self.ymax,1)

        for y in ylist:
            self.ax.plot([int(xmin),int(xmax)], [y,y], **plot_kwargs)
            


    def draw_xticks(self, ticks=None, dy=0.1, **plot_kwargs):
        kwargs = {'color':'k',\
                  'linewidth':2}
        kwargs.update(plot_kwargs)

        if ticks is None:
            ticks = np.arange(int(self.xmin), int(self.xmax), 1)

        
        for tick in ticks:
            start_tick = [tick, dy]
            end_tick = [tick, -dy]
            self.ax.plot([tick,tick], [dy,-dy], **kwargs)


    def draw_yticks(self, ticks=None, dx=0.1, **plot_kwargs):
        kwargs = {'color':'k',\
                  'linewidth':2}
        kwargs.update(plot_kwargs)

        if ticks is None:
            ticks = np.arange(int(self.ymin), int(self.ymax), 1)

        
        for tick in ticks:
            self.ax.plot([-dx,dx], [tick,tick], **kwargs)
            
            
