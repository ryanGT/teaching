from matplotlib.pyplot import *
from numpy import *
import numpy as np
import control
from control import TransferFunction as TF
import copy

font_size = 20.0

def _digit_coeffs_to_C_array_str(coeff_list, N, fmt='%0.8g'):
    out_str = '{'
    m = len(coeff_list)
    n_pad = N-m

    if n_pad > 0:
        pad_str = '0,'*n_pad
        out_str += pad_str

    for i, coeff in enumerate(coeff_list):
        cur_str = fmt % coeff
        out_str += cur_str
        if i < m-1:
            out_str += ','

    out_str+= '};'
    return out_str
            

def digital_TF_to_arduino_arrays(TFz, sub_str=''):
    den = np.squeeze(TFz.den)
    num = np.squeeze(TFz.num)
    n = len(den)
    m = len(num)

    a_str = _digit_coeffs_to_C_array_str(den, n)
    if sub_str:
        a_lhs = 'a_' + sub_str
        b_lhs = 'b_' + sub_str
    else:
        a_lhs = 'a'
        b_lhs = 'b'
    a_str = '%s = %s' % (a_lhs, a_str)
    b_str = _digit_coeffs_to_C_array_str(num, n)
    b_str = '%s = %s' % (b_lhs, b_str)
    print(b_str)
    print(a_str)
    

def _unpack_complex(root_list):
    """If there are any complex roots, they are specify as tuples
    using (wn,z).  Find those and put -z*wn+/-j*wd in the output list."""    
    roots_out = []
    for root in root_list:
        curtype = type(root)
        if np.isscalar(root):
            roots_out.append(root)
        elif curtype in [list, tuple]:
            wn = root[0]
            z = root[1]
            assert np.abs(z) < 1, "Overdamped roots are not handled at this time"
            wd = wn*np.sqrt(1-z**2)
            r1 = -z*wn+1j*wd
            r2 = np.conj(r1)
            roots_out.extend([r1,r2])
        else:
            print("I don't know how to deal with this root type: %s" % root)
    return roots_out


def second_order_roots_to_tuple(root_list):
    """If there are any second order roots in root_list, pop them as
    complex conjugate pairs and replace with (wn,z).  This is a
    stepping stone toward print factored latex for a TF and it is the
    opposite of the function _unpack_complex"""
    list_out = []
    mylist = copy.copy(root_list.tolist())
    N = len(root_list)

    for i in range(N):
        if len(mylist) == 0:
            break
        cur_root = mylist.pop()
        if np.abs(np.imag(cur_root)) > 1e-6:
            # this root is complex
            myconj = np.conj(cur_root)
            ci = mylist.index(myconj)
            mylist.pop(ci)
            wn = np.abs(cur_root)
            z = -np.real(cur_root)/wn
            list_out.append((wn,z))
        else:
            list_out.append(cur_root)

    return list_out


def one_root_to_latex(root_in):
    if np.isscalar(root_in):
        assert np.abs(np.imag(root_in)) < 1e-6, "not sure if this is real: %s" % root_in
        if np.abs(root_in) < 1e-6:
            str_out = 's'
        else:
            str_out = 's %+0.4g' % -np.real(root_in)
    else:
        wn = root_in[0]
        z = root_in[1]
        b = 2*z*wn
        c = wn**2
        str_out = 's^2 %+0.4g s %+0.4g' % (b,c)
    return str_out

    

def root_list_to_latex(pole_list):
    """pole_list is assumed to be a list of first poles or zeros along
    with (wn,z) tuples.  If an entry is scalar, it is a first order
    root."""
    str_out = ""
    for p in pole_list:
        cur_str = one_root_to_latex(p)
        if len(pole_list) == 1:
            return cur_str
        else:
            str_out += '(%s)' % cur_str
    return str_out



def TF_to_factored_latex(G,lhs=None,substr=None):
    """Convert a TF instance to latex where the numerator and
    denominator are factored into first and second order terms."""
    p_list = second_order_roots_to_tuple(G.pole())
    z_list = second_order_roots_to_tuple(G.zero())
    if not z_list:
        z_str = '1'
    else:
        z_str = root_list_to_latex(z_list)
    p_str = root_list_to_latex(p_list)
    rhs = '\\frac{%s}{%s}' % (z_str,p_str)
    if substr is not None:
        if lhs is None:
            lhs = 'G_{%s}(s)' % substr
        else:
            lhs = '%s_{%s}(s)' % (lhs,substr)
            
    if lhs is not None:
        out_str = '%s = %s' % (lhs, rhs)
        return out_str
    else:
        return rhs
    
    
def build_TF(poles=[], zeros=[]):
    """Build a TF whose poles and zeros are given.  Complex poles or zeros
    are created by passing (wn,z) as a tuple in the pole or zero list."""
    if np.isscalar(poles):
        poles = [poles]
    if np.isscalar(zeros):
        zeros = [zeros]
        
    all_poles = _unpack_complex(poles)
    all_zeros = _unpack_complex(zeros)
    num = np.poly(all_zeros)
    den = np.poly(all_poles)
    G = TF(num,den)
    return G
    
    
def my_rlocus(G, k):
    rmat, kout = control.root_locus(G, k, Plot=False)
    plot(real(rmat), imag(rmat))
    poles = G.pole()
    plot(real(poles), imag(poles), 'x')
    zeros = G.zero()
    if len(zeros) > 0:
        plot(real(zeros), imag(zeros), 'o')

def TF_mag(G, s1):
    """Find the magnitude of transfer function G at point s1.  G is
    expected to be a control.TransferFunction instance."""
    N_poly = poly1d(squeeze(G.num))
    D_poly = poly1d(squeeze(G.den))
    G_comp = N_poly(s1)/D_poly(s1)
    G_mag = abs(G_comp)
    return G_mag



def plot_settling_lines(fignum, p=2.0, plotstr='k--'):
    """Plot lines of +/-p% to help determine the settling time of a
    step response."""
    figure(fignum)
    myx = xlim()
    p2 = float(p)/100
    plot(myx, [1.0-p2,1.0-p2], plotstr, label=None)
    plot(myx, [1.0+p2,1.0+p2], plotstr, label=None)
    

def draw_constant_zeta_lines(fignum, z, r=100):
    figure(fignum)
    x = -sin(z)*r
    y = cos(z)*r
    plot([0,x],[0,y],'k--', label=None)
    plot([0,x],[0,-y],'k--', label=None)
    

def plot_sigma_line(fignum, sig, plotstr='k-.'):
    """Plot lines of s=-sig on a root locus to help determine the
    settling time of a step response."""
    figure(fignum)
    myy = ylim()
    plot([-sig,-sig], myy, plotstr, label=None)


def calc_line_between_points(start, end, start_p=0.1, end_p=0.6):
    delta = end-start
    line_start = start_p*delta + start
    line_end = end_p*delta + start
    return line_start, line_end


def draw_line_between_points(start, end, plotstr='k:', **kwargs):
    line_start, line_end = calc_line_between_points(start, end, **kwargs)
    plot([real(line_start), real(line_end)], \
         [imag(line_start), imag(line_end)], plotstr)


def draw_horiz_line(point, d1, d2, plotstr='k:'):
    x1 = real(point) + d1
    x2 = real(point) + d2
    y = imag(point)
    plot([x1,x2], [y,y], plotstr)

def label_angle(point, label, dr, di):
    text(real(point) + dr, imag(point) + di, label, size=font_size)


def label_test_point(s1, label='$s_1$', dr=2, di=2):
    text(real(s1) + dr, imag(s1) + di, label, size=font_size)


def calc_angle(s1, point):
    diff = s1-point
    deg = angle(diff,1)
    return deg


def draw_point(point, marker, markersize=10):
    plot([real(point)],[imag(point)],marker,ms=markersize)

def draw_zero(zero):
    """Call draw_point with marker set to 'ro'"""
    draw_point(zero, marker='ro')

def draw_pole(pole):
    """Call draw_point with marker set to 'b^'"""
    draw_point(pole, marker='b^')
    
def draw_angle_lines(s1, point, start_p=0.1, end_p=0.6, plotstr='k:'):
    draw_line_between_points(point, s1, plotstr=plotstr, \
                             start_p=start_p, end_p=end_p)


def calc_angle_list(s1, point_list):
    angle_list = []
    for point in point_list:
        cur_angle = calc_angle(s1, point)
        angle_list.append(cur_angle)

    return angle_list

def calc_psi_and_phi_lists(s1, TF):
    zeros_a = TF.zero()#this returns an array
    zeros = zeros_a.tolist()
    zeros.reverse()#arrays don't have the reverse method that lists do
    poles_a = TF.pole()
    poles = poles_a.tolist()
    poles.reverse()

    psi_list = calc_angle_list(s1, zeros)
    phi_list = calc_angle_list(s1, poles)
    return psi_list, phi_list
    

                              
def plot_points_and_angles(fignum, s1, P, ms=8, msp=10, \
                           start_p=0.1, end_p=0.6, \
                           za_labels=None, pa_labels=None,
                           dr=0.25, di=0.5):
    """start_p is the percentage distance along the line between a
    pole or zero and s1 where the angle line starts.  end_p is the
    percentage where the angle line ends.

    za_labels are the labels for the zero angles.
    pa_labels are the labels fro the pole angles."""
    zeros = P.zero()
    poles_a = P.pole()
    poles = poles_a.tolist()
    poles.reverse()
    print('poles: ' + str(poles))
    figure(fignum)
    plot([real(s1)],[imag(s1)],'gs',ms=ms)

    if za_labels is None:
        za_labels = []
        for i in range(len(zeros)):
            n = i + 1
            curlabel = '$\\psi_%i$' % n
            za_labels.append(curlabel)

    if pa_labels is None:
        pa_labels = []
        for i in range(len(poles)):
            n = i + 1
            curlabel = '$\\phi_%i$' % n
            pa_labels.append(curlabel)

    
    d1 = 0.5
    d2 = 2.0

    psi_list = []
    for zero, curlabel in zip(zeros, za_labels):
        plot([real(zero)],[imag(zero)],'ro',ms=ms)
        draw_line_between_points(zero, s1, start_p=start_p, end_p=end_p)
        draw_horiz_line(zero, d1, d2)
        label_angle(zero, curlabel, dr, di)
        cur_psi = calc_angle(s1, zero)
        psi_list.append(cur_psi)

    phi_list = []
    for pole, curlabel in zip(poles, pa_labels):
        draw_pole(pole)
        draw_line_between_points(pole, s1, start_p=start_p, end_p=end_p)
        draw_horiz_line(pole, d1, d2)
        label_angle(pole, curlabel, dr, di)
        cur_phi = calc_angle(s1, pole)
        phi_list.append(cur_phi)

    label_test_point(s1, dr=dr, di=di*0.5)
    return psi_list, phi_list


def create_swept_sine_signal(fmax=20.0, fmin=0.0, \
                             tspan=10.0, dt=1.0/500, \
                             t=None, deadtime=0.0):
    """Create a sweptsine signal

    u = sin(2*pi*f*t)
    
    whose frequency fstarts at fmin and ends at fmax.  The signal will
    have a time span of tspan and a time step of dt.  Alternatvely,
    passing in a t vector sets tspan and dt.  deadtime would most
    likely be used experimentally to provide time at the start and end
    of the test where u is zero (basically padding the input with
    deadtime)."""
    if t is not None:
        dt = t[1] - t[0]
        tspan = t.max() - t.min() + dt - deadtime*2.0
    else:
        t = arange(0,tspan,dt)
        
    slope = (fmax-fmin)/tspan
    f = fmin + slope*t
    u = sin(2*pi*f*t)

    if deadtime> 0.0:
        deadt = arange(0,deadtime, dt)
        zv = zeros_like(deadt)
        u = r_[zv, u, zv]
        N = len(u)
        nvect = arange(N)
        t = dt*nvect

    return u, t

    
def create_freq_vect(timevect):
    tspan = timevect.max()-timevect.min()
    N = timevect.shape[0]
    dt = tspan/(N-1)
    fs = 1.0/dt
    T = tspan+dt
    df = 1.0/T
    nvect = arange(N)
    f = df*nvect
    return f

