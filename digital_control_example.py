from matplotlib.pyplot import *
from scipy import *

import control
import bode_utils

G = control.TransferFunction(100.0,[1,0,0])#100.0/s**2

f = logspace(-2,2,1000)
w = 2*pi*f

db, phase, f2 = control.bode(G, omega=w, dB=True, Hz=True, Plot=False)

bode_utils.bode_plot(f, db, phase, clear=True, fignum=1, label='$G$')

#Choose freq and design a lead comp.
f_c = 10.0
w_c = 2*pi*f_c
factor = 5.0
z = w_c/factor
p = w_c*factor
G_lead = control.TransferFunction([1,z],[1,p])*p/z

gain = 6.0

db2, phase2, f2 = control.bode(G*G_lead*gain, omega=w, dB=True, Hz=True, Plot=False)

bode_utils.bode_plot(f, db2, phase2, clear=False, fignum=1, label='$G_c \\cdot G$')

subplot(211)
legend(loc=3)

subplot(212)
ylim([-200,-100])

#find digital coefficients
import digital_control
b, a = digital_control.c2d_tustin(G_lead*gain)
print('b = ' + str(b))
print('a = ' + str(a))


show()

