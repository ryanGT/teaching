from matplotlib.pyplot import *
from scipy import *
import bode_utils
import matplotlib

rcParams['figure.subplot.bottom'] = 0.15

myfreqlims = [10**-2,10**3]

fig = figure(1)
fig.clf()
ax1 = subplot(211)
ax1.set_xscale('log')
ax1.set_ylabel('dB Mag.\n\n')
ax1.set_xlim(myfreqlims)
ax1.set_ylim([-60,60])
ax1.set_yticks(np.arange(-60,60,20))
bode_utils.mygrid(ax1)
ax1.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
ax1.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
#grid(1)

def blank_x_labels(ax):
    myticks = ax.get_xticks()
    N = len(myticks)
    empty_labels = ['']*N
    ax.set_xticklabels(empty_labels)

def blank_y_labels(ax):
    myticks = ax.get_yticks()
    N = len(myticks)
    empty_labels = ['']*N
    ax.set_yticklabels(empty_labels)

#blank_x_labels(ax1)
#blank_y_labels(ax1)

ax2 = subplot(212)
ax2.set_xscale('log')
#grid(1)
ax2.set_ylabel('Phase (deg.)\n\n')
ax2.set_xlabel('\n\n Freq. (Hz)')
ax2.set_xlim(myfreqlims)
ax2.set_ylim([-360,0])
ax2.set_yticks(np.arange(-360,360,90))
bode_utils.mygrid(ax2)
ax2.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
ax2.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())

#blank_x_labels(ax2)
#blank_y_labels(ax2)

#bode_utils.mygrid(ax2)

tight_layout()

import pylab_util as PU
PU.mysave('blank_Bode.eps')


#rcParams['figure.subplot.bottom'] = 0.18

## fig = figure(2, (8,5))
## fig.clf()
## ax = fig.add_subplot(111)
## ax.set_xscale('log')
## grid(1)
## ax.set_ylabel('dB Mag.\n\n')
## blank_x_labels(ax)
## blank_y_labels(ax)
## ax.set_xlabel('\n\n Freq. (Hz)')
#PU.mysave('blank_dB_mag.pdf')

show()

