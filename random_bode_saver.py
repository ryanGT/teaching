import os
import txt_mixin
import numpy as np
import importlib

saved_path = '/Users/kraussry/git/teaching/random_bodes_saved.py'


def get_N():
    if not os.path.exists(saved_path):
        N = 0
    else:
        import random_bodes_saved
        importlib.reload(random_bodes_saved)
        N = len(random_bodes_saved.G_list)
    return N


def get_list(N):
    if N == 0:
        mylist = ['import control','G_list = []', '']
    else:
        myfile = txt_mixin.txt_file_with_list(saved_path)
        mylist = myfile.list
    return mylist

    
def G_to_text(G, N):
    ns = np.squeeze(G.num)
    ds = np.squeeze(G.den)
    numstr = np.array2string(ns,separator=',')
    denstr = np.array2string(ds,separator=',')
    num2 = 'num%i = %s' % (N, numstr)
    den2 = 'den%i = %s' % (N, denstr)
    Gstr = 'G%i = control.TransferFunction(num%i,den%i)' % \
               (N, N, N)
    append_line = 'G_list.append(G%i)' % N
    lines_out = [num2,den2,Gstr, append_line]
    return lines_out


def save_G(G,N=None):
    if N is None:
        N = get_N()
    mylist = get_list(N)
    new_lines = G_to_text(G, N)
    mylist.append('')
    mylist.extend(new_lines)
    txt_mixin.dump(saved_path, mylist)
    return N

