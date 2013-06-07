#from matplotlib.pyplot import *
#from scipy import *
from numpy import *

import control


def _c2d_sub(G_s, numsub, densub, scale):
    """This method performs substitutions for continuous to
    digital conversions using the form:

                numsub
    s = scale* --------
                densub

    where scale is a floating point number and numsub and densub
    are poly1d instances.

    For example, scale = 2.0/T, numsub = poly1d([1,-1]), and
    densub = poly1d([1,1]) for a Tustin c2d transformation."""
    num_array = squeeze(G_s.num)
    den_array = squeeze(G_s.den)
    num = poly1d(num_array)
    den = poly1d(den_array)
    m = num.order
    n = den.order
    mynum = 0.0
    for p, coeff in enumerate(num.coeffs):
        mynum += poly1d(coeff*(scale**(m-p))*((numsub**(m-p))*(densub**(n-(m-p)))))
    myden = 0.0
    for p, coeff in enumerate(den.coeffs):
        myden += poly1d(coeff*(scale**(n-p))*((numsub**(n-p))*(densub**(n-(n-p)))))
    return mynum.coeffs, myden.coeffs


def c2d_tustin(G_s, dt=1.0/500, a=2.0):
    """Convert continuous transfer function G(s) to a digital one G(z)
    using the Tustin approach.  Note that his is good for
    compensators, not for plants.  The conversion is done by substituting

        a  z-1
    s = - -----
        T  z+1

    into the compensator, where a is typically 2.0"""
    scale = a/dt
    numsub = poly1d([1.0,-1.0])
    densub = poly1d([1.0,1.0])
    mynum, myden = _c2d_sub(G_s,numsub, densub, scale)
    mynum = mynum/myden[0]
    myden = myden/myden[0]
    return mynum, myden


    
if __name__ == '__main__':
    Gcs1 = control.TransferFunction([1,2],[1,11])*29.0
    b1, a1 = c2d_tustin(Gcs1,dt=0.1)
    #from Dorsey, bottom of page 496
    a1_d = -0.2903
    b0_d = 20.6
    b1_d = -0.8182*20.6
    test1_b = b1 - array([b0_d, b1_d])
    test1_a = a1 - array([1.0,a1_d])
    
