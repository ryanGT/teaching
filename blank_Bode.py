from matplotlib.pyplot import *
from scipy import *

fig = figure(1)
fig.clf()
ax1 = subplot(211)
ax1.set_xscale('log')
grid(1)
ax1.set_ylabel('dB Mag.\n')

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

blank_x_labels(ax1)
blank_y_labels(ax1)

ax2 = subplot(212)
ax2.set_xscale('log')
grid(1)
ax2.set_ylabel('Phase (deg.)\n')
ax2.set_xlabel('\n Freq. (Hz)')

blank_x_labels(ax2)
blank_y_labels(ax2)

import pylab_util as PU
PU.mysave('blank_Bode.eps')

show()

