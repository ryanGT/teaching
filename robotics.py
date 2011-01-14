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


def HT4(axis='',angle=0,x=0.,y=0.,z=0.):
    #4x4 homogenous transformation matrix
    if axis:
        r1=rot3by3(axis,angle)
    else:
#        r1=scipy.eye(3,'f')
        r1=scipy.eye(3,dtype='f')
    s1=c_[r1,array([[x],[y],[z]])]
    return r_[s1,array([[0.,0.,0.,1.]])]

