import numpy as np
import robotics
from numpy import pi, sin, cos, tan, arctan2
dtr = pi/180
rtd = 180/pi

import var_to_latex


def matrix_to_latex(matin, lhs="^0_{tip}\\mathbf{T}", dollar_signs=True):
    out = var_to_latex.ArrayToLaTex(matin, lhs)
    if dollar_signs:
        out = "$$%s$$" % out
    print(out)


def matrix_to_starter_code(matin, lhs="T0tip", fmt="%0.5g"):
    out_str = lhs + " = np.array(["
    tail = "])"
    row_num = 0
    nr,nc = matin.shape
    ws = " "*len(out_str)#white space for subsequent rows
    for row in matin:
        row_str = "["
        for ent in row:
            if len(row_str) > 1:
                #second or later entry
                row_str += ", "
            ent_str = fmt % ent
            row_str += ent_str
        row_str += "]"
        if row_num < (nr-1):
            row_str += ","
        row_str += "\n"
        if row_num > 0:
            row_str = ws + row_str
        row_num += 1
        out_str += row_str
    out_str = out_str.rstrip()
    out_str += tail
    print(out_str)
    
    
