from numpy import *
import copy

deg_to_rad = pi/180.0
rad_to_deg = 180.0/pi


def clean_small_floats(matin, tol=1e-6):
    """Replace all entries whose absolute value is smaller than tol
    with 0.0"""
    rows, cols = where(abs(matin) < 1e-6)
    matin[rows,cols] = 0.0
    return matin

def prettymat(matin):
    tol = 1e-6
    inds = np.where(abs(matin)<tol)
    matout = copy.copy(matin)
    matout[inds] = 0
    return matout


def cosd(theta):
    theta_r = theta*deg_to_rad
    return cos(theta_r)


def sind(theta):
    theta_r = theta*deg_to_rad
    return sin(theta_r)


def Rz(theta_d):
    """Given input theta_d in degrees, find the Rz matrix."""
    rad = theta_d*pi/180.
    R = array([[cos(rad),-sin(rad),0.0],\
               [sin(rad),cos(rad),0.0],\
               [0.0,0.0,1.0]])
    return R


def Rx(theta_d):
    """Given input theta_d in degrees, find the Rx matrix."""
    rad = theta_d*pi/180.
    R = array([[1.0,0.0,0.0],\
               [0.0,cos(rad),-sin(rad)],\
               [0.0,sin(rad),cos(rad)]])
    return R


def Ry(theta_d):
    """Given input theta_d in degrees, find the Ry matrix."""
    rad = theta_d*pi/180.
    R = array([[cos(rad),0.0,sin(rad)],\
               [0.0,1.0,0.0],\
               [-sin(rad),0.0,cos(rad)]])
    return R


def HT_from_R_and_Porg(R_mat, PBorgA):
    """Given a 3x3 rotation matrix R_mat and a 3x1 vector of the
    origin of frame B expressed in frame A, PBorgA, return the 4x4 HT
    matrix."""
    temp = column_stack([R_mat,PBorgA])
    HT = row_stack([temp,[0,0,0,1]])
    return HT



def HTinv(Tin):
    Tout = eye(4)
    R = Tin[0:3,0:3]
    Ri = R.T
    Tout[0:3,0:3] = Ri
    P_BorgA = Tin[0:3,3]
    P_AorgB = -1.0*dot(Ri,P_BorgA)
    Tout[0:3,3] = P_AorgB
    return Tout



def HTz(angle=0,x=0.,y=0.,z=0.):
    R = Rz(angle)
    HT = HT_from_R_and_Porg(R, [x,y,z])
    return HT


def HTx(angle=0,x=0.,y=0.,z=0.):
    R = Rx(angle)
    HT = HT_from_R_and_Porg(R, [x,y,z])
    return HT


def HTy(angle=0,x=0.,y=0.,z=0.):
    R = Ry(angle)
    HT = HT_from_R_and_Porg(R, [x,y,z])
    return HT


def DH(alpha=0.0, a=0.0, theta=0.0, d=0.0):
    alpha_r = alpha*pi/180.0
    theta_r = theta*pi/180.0
    T = array([[cos(theta_r),-sin(theta_r), 0, a], \
               [sin(theta_r)*cos(alpha_r), cos(theta_r)*cos(alpha_r),-sin(alpha_r),-sin(alpha_r)*d], \
               [sin(theta_r)*sin(alpha_r), cos(theta_r)*sin(alpha_r), cos(alpha_r), cos(alpha_r)*d],\
               [0,0,0,1]])
    return T
