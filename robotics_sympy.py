import sympy
from sympy import Matrix, cos, sin, eye

def Rx(th):
    R = Matrix([[1.0,0.0,0.0],\
                [0.0,cos(th),-sin(th)],\
                [0.0,sin(th),cos(th)]])
    return R

def HT(R, Px=0.0, Py=0.0, Pz=0.0):
    T = eye(4)
    T[0:3,0:3] = R
    T[0,3] = Px
    T[1,3] = Py
    T[2,3] = Pz
    return T


def HTx(alpha, Px=0.0, Py=0.0, Pz=0.0):
    R = Rx(alpha)
    T = HT(R, Px, Py, Pz)
    return T

    
def Rz(th):
    R = Matrix([[cos(th),-sin(th),0.0],\
                [sin(th),cos(th),0.0],\
                [0.0,0.0,1.0]])
    return R


def HTz(theta, Px=0.0, Py=0.0, Pz=0.0):
    R = Rz(theta)
    T = HT(R, Px, Py, Pz)
    return T
