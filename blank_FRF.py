from pylab import *
from scipy import *
import matplotlib
import pylab_util

rcParams['ytick.color'] = 'b'
rcParams['text.usetex'] = False

import os

figure(1)
clf()
myprops = matplotlib.text.FontProperties(size=24)

def one_axis():
    grid(1)
    xarray = arange(-1,1,0.2)
    xlabels = ['']*5 + [''] + ['']*4
    yarray = arange(-1,1,0.4)
    ylabels = ['']*len(yarray)

    xticks(xarray, xlabels, color=(0,0,0), fontproperties=myprops)
    yticks(yarray, ylabels, color=(0,0,0), fontproperties=myprops)


    myxlabel = ''
    myylabel = ''
    xlabel(myxlabel)
    ylabel(myylabel)

subplot(211)
one_axis()
ylabel('Magnitude \n')

subplot(212)
one_axis()
ylabel('Phase (degrees) \n')



filename = 'blank_FRF.eps'
outdir = '/home/ryan/siue/classes/452/2011/final_exam/'
outpath = os.path.join(outdir, filename)
pylab_util.mysave(outpath)

show()
