from pylab import *
from scipy import *

figure(1)
xticks(arange(0,1.1,0.2))
grid(1)
yticks(arange(-10,10.5,1), \
       ['-10','','-8','','-6','','-4','','-2','','0', \
        '','2','','4','','6','','8','','10'])
ylabel('$\\theta$ (counts)')
xlabel('Time (sec)')

show()
