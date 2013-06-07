from pylab import *
from numpy import *

font_size = 20.0

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
