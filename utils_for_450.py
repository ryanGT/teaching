from pylab import *
from scipy import *

import controls

def make_G_list(zetas, omegas):
    G_list = [] 
    for z, w in zip(zetas, omegas):
        G = controls.TransferFunction(w**2, [1,2*w*z,w**2])
        G_list.append(G)
    return G_list


def find_poles(G_list):
    for G in G_list:
        print('-------------')
        for pole in G.poles:
            wn = abs(pole)
            wd = imag(pole)
            sigma = -real(pole)
            zeta = sigma/wn
            print('   s = '+str(pole))
            print('  wn = %0.4g' % wn)
            print('zeta = %0.4f' % zeta)
            print('  wd = %0.4g' % wd)
    print('-----------')
    
def pole_locs_and_step_response(G_list, t=None, startfi=1):
    if t is None:
        t = arange(0,5,0.01)
##     wd_vect = omegas*sqrt(1-zetas**2)
##     s_vect1 = -1*zetas*omegas+1.0j*wd_vect
##     s_vect2 = conj(s_vect1)

    figure(startfi)
    clf()
##     plot(real(s_vect1), imag(s_vect1), 'b^')
##     plot(real(s_vect2), imag(s_vect2), 'g^')
    
    first = 1

    fi = startfi+1
    colors = 'bgrk'

    n = 0
    leglist = []
    for G in G_list:
        figure(startfi)
        fmt = colors[n]+'^'
        plot(real(G.poles), imag(G.poles), fmt)
        text(real(G.poles[0]), imag(G.poles[0]), '$G_%i$' % (n+1))
##         print('-----------------')
##         print('w='+str(w))
##         print('z='+str(z))
##         wd = w*sqrt(1-z**2)
##         print('wd='+str(wd))
##         print('poles:'+str(G.poles))

        if first:
            G.step_response(t, fignum=fi)
            first = 0
        else:
            G.step_response(t, fignum=fi, clear=False)
        n += 1
        leglist.append('$G_%i$' % n)

    figure(startfi)
    legend(leglist,1)

    figure(startfi+1)
    legend(leglist,4)
