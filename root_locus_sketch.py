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
    def __init__(self, ax=None, \
                 xmax=2, xmin=-5.5, ymax=5.5, ymin=-5.5, \
                 xlims=[-8,4], ylims=[-6,6], \
                 fontdict = {'size': 20, 'family':'serif'}, \
                 axis_lw=2, \
                 ):
        if ax is None:
            fig = plt.figure(figsize=(9,9))
            ax = fig.add_subplot(111)
        self.ax = ax
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.xlims = xlims
        self.ylims = ylims
        self.axis_lw = axis_lw
        self.fontdict = fontdict
        
        

    def draw_arrow(self, start_coords, end_coords, \
                   fc='k', ec=None, lw=None, **plot_args):
        if not hasattr(self, 'hw'):
            self.set_arrow_lengths()
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


    def draw_marker(self, point, style='go', size=12, **plot_kwargs):
        self.ax.plot([np.real(point)],[np.imag(point)], \
                     style, markersize=size, **plot_kwargs)


    def add_text(self, point, text, xoffset=0, yoffset=0, \
                 fontdict=None):
        if fontdict is None:
            fontdict = self.fontdict
        self.ax.text(np.real(point)+xoffset, np.imag(point)+yoffset, \
                     text, fontdict=fontdict)


    def add_math_text(self, point, text, *args, **kwargs):
        if text[0] != '$':
            text = '$%s$' % text
        self.add_text(point, text, *args, **kwargs)
            

    def draw_point_with_label(self, point, text, style='go', size=12, \
                          xoffset=0, yoffset=0, \
                          fontdict=None):
        self.draw_marker(point, style=style, size=size)
        self.add_text(point, text, xoffset=xoffset, yoffset=yoffset, \
                      fontdict=fontdict)


    def draw_line(self, start, end, linestyle='k--', **plot_kwargs):
        self.ax.plot([np.real(start), np.real(end)], \
                     [np.imag(start), np.imag(end)], \
                     linestyle, **plot_kwargs)


    def draw_lines_to_point(self, point, pole_or_zero_list, \
                            linestyle='k--', **plot_kwargs):
        for pz in pole_or_zero_list:
            self.draw_line(pz, point, linestyle=linestyle, **plot_kwargs)
            

    def draw_poles(self, pole_list, style='rX', size=12, **plot_kwargs):
        for i, p in enumerate(pole_list):
            j = i+1
            self.ax.plot([np.real(p)],[np.imag(p)], \
                         style, markersize=size, **plot_kwargs)


    def draw_zeros(self, zero_list, style='ro', size=12, **plot_kwargs):
        self.draw_poles(zero_list, style=style, size=size, **plot_kwargs)
        

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
            ticks = np.arange(int(self.ymin), int(self.ymax)+1, 1)

        
        for tick in ticks:
            self.ax.plot([-dx,dx], [tick,tick], **kwargs)
            

    def main_axis(self):
        self.set_arrow_lengths()
        self.axis_off()
        self.draw_axis()
        self.draw_xticks()
        self.draw_yticks()
        self.label_axes()
        self.ax.set_xlim(self.xlims)
        self.ax.set_ylim(self.ylims)
        plt.tight_layout()
            


class root_locus_sketch_with_TF(root_locus_sketch):
    def __init__(self, ax, G, *args, **kwargs):
        root_locus_sketch.__init__(self, ax, *args, **kwargs)
        self.G = G
        

    

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
            


class root_locus_sketch_with_TF_2(root_locus_sketch):
    def __init__(self, ax, G, *args, **kwargs):
        root_locus_sketch.__init__(self, ax, *args, **kwargs)
        self.G = G

    
    def draw_poles(self, style='rX', size=12, zorder=10, **kwargs):
        root_locus_sketch.draw_poles(self, self.G.pole(), style=style, \
                                     size=size, zorder=zorder, **kwargs)

        
    def draw_zeros(self, style='ro', size=12, zorder=10, **kwargs):
        root_locus_sketch.draw_poles(self, self.G.zero(), style=style, \
                                     size=size, zorder=zorder, \
                                     **kwargs)
        


    def add_test_point(self, point, style='go', size=12, \
                       label=None, label_offset=0+0j, \
                       **plot_kwargs):
        self.s0 = point
        self.draw_marker(point, style=style, size=size, **plot_kwargs)
        if label is not None:
            self.add_math_text(self.s0+label_offset, label)
            

    def draw_lines_to_test_point(self, linestyle='k--', **plot_kwargs):
        self.draw_lines_to_point(self.s0, self.G.pole(), \
                                 linestyle=linestyle, **plot_kwargs)
        self.draw_lines_to_point(self.s0, self.G.zero(), \
                                 linestyle=linestyle, **plot_kwargs)


    def build_label_list(self, N, pat):
        labels = []
        for i in range(N):
            j = i+1
            cur_str = pat % j
            labels.append(cur_str)
        return labels

        
    def make_phi_labels(self):
        N = len(self.G.pole())
        phi_labels = self.build_label_list(N, '\\phi_{%i}')
        return phi_labels


    def make_psi_labels(self):
        N = len(self.G.zero())
        psi_labels = self.build_label_list(N, '\\psi_{%i}')
        return psi_labels


    def label_angles_to_point(self, phi_labels, psi_labels, \
                              phi_offsets=None, psi_offsets=None, \
                              **kwargs):
        if phi_offsets is None:
            np = len(self.G.pole())
            phi_offsets = [0]*np
        if psi_offsets is None:
            nz = len(self.G.zero())
            psi_offsets = [0]*nz
        
        for p, label, po in zip(self.G.pole(), phi_labels, phi_offsets):
            self.add_math_text(p+po, label, **kwargs)
        for z, label, zo in zip(self.G.zero(), psi_labels, psi_offsets):
            self.add_math_text(z+zo, label, **kwargs)
            


class root_locus_sketch_two_pole_locations(root_locus_sketch):
    """A class for generating pole locations plots for comparing two
    TFs and their step responses."""
    def __init__(self, G1, G2, label_offsets=[0.2+0.2j, 0.2+0.2j], \
                 markers=['bo','g^'], inds=[1,2], \
                 **kwargs):
        root_locus_sketch.__init__(self, **kwargs)
        self.G1 = G1
        self.G2 = G2
        self.label_offsets = label_offsets
        self.markers = markers
        self.inds = inds


    def draw_and_label_poles(self):
        # get poles and force the imaginary part to be positive
        p1 = self.G1.pole()[0]
        p2 = self.G2.pole()[0]

        for p, m, lo, ind in zip([p1,p2], self.markers, \
                                  self.label_offsets, self.inds):
            p = np.real(p) + 1j*np.abs(np.imag(p))
            self.draw_marker(p, style=m)
            self.draw_marker(np.conj(p), style=m)
            mytext = '$G_{%i}$' % ind
            self.add_text(p, mytext, xoffset=np.real(lo), yoffset=np.imag(lo))
        

    def main(self):
        self.main_axis()
        self.draw_and_label_poles()
        
