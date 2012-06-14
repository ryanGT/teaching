from scipy import *

def rot3by3(axis,angle):
    rad=angle*pi/180.
    if isinstance(axis,str):
        if axis.lower()=='x':
            axis=1
        elif axis.lower()=='y':
            axis=2
        elif axis.lower()=='z':
            axis=3
    if axis==1:
        R=array([[1.0,0.0,0.0],[0.0,cos(rad),-sin(rad)],[0.0,sin(rad),cos(rad)]])
    elif axis==2:
        R=array([[cos(rad),0.0,sin(rad)],[0.0,1.0,0.0],[-sin(rad),0.0,cos(rad)]])
    elif axis==3:
        R=array([[cos(rad),-sin(rad),0.0],[sin(rad),cos(rad),0.0],[0.0,0.0,1.0]])
    return R


def Rz(theta):
    return rot3by3('z',theta)


def Rx(theta):
    return rot3by3('x',theta)


def Ry(theta):
    return rot3by3('y',theta)


def HT4(axis='',angle=0,x=0.,y=0.,z=0.):
    #4x4 homogenous transformation matrix
    if axis:
        r1=rot3by3(axis,angle)
    else:
#        r1=scipy.eye(3,'f')
        r1=scipy.eye(3,dtype='f')
    s1=c_[r1,array([[x],[y],[z]])]
    return r_[s1,array([[0.,0.,0.,1.]])]


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
    return HT4('z',angle=angle, x=x, y=y, z=z)


def HTx(angle=0,x=0.,y=0.,z=0.):
    return HT4('x',angle=angle, x=x, y=y, z=z)


def HTy(angle=0,x=0.,y=0.,z=0.):
    return HT4('y',angle=angle, x=x, y=y, z=z)
