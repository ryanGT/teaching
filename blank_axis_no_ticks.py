from pylab import *
from scipy import *
import matplotlib
import pylab_util

import os

figure(1)
plot([0,0],[-1,1],'k-')
plot([-1,1],[0,0],'k-')

myprops = matplotlib.text.FontProperties(size=24)

grid(1)
myarray = arange(-1,1,0.2)
#mylabels = ['']*5 + ['0'] + ['']*4
mylabels = ['']*5 + [''] + ['']*4

xticks(myarray, mylabels, color=(0,0,0), fontproperties=myprops)
yticks(myarray, mylabels, color=(0,0,0), fontproperties=myprops)
#myxlabel = '$x_1$'
#myylabel = '$x_2$'
myxlabel = ''
myylabel = ''
xlabel(myxlabel)
ylabel(myylabel)

filename = 'blank_phase_portrait.eps'
outdir = '/home/ryan/nonlinear_controls_2011/midterm/'
outpath = os.path.join(outdir, filename)
pylab_util.mysave(outpath)

fno, ext = os.path.splitext(filename)
filename1 = fno + '.pdf'
filename2 = 'cropped_blank_phase_portrait.pdf'
curdir = os.getcwd()
os.chdir(outdir)
cmd = 'pdfcrop %s %s' % (filename1, filename2)
os.system(cmd)
os.chdir(curdir)

show()
