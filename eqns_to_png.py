import os, glob
import sympy
from sympy.interactive import printing
printing.init_printing(use_latex=True)

from IPython import display
from IPython.display import Math

myheader = r"""\documentclass[12pt]{article}
\newcommand{\be}{\begin{equation}}
\newcommand{\ee}{\end{equation}}
\newcommand{\M}[1]{\mathbf{#1}}
\newcommand{\myvector}[3]{\left\{\begin{array}{c}#1\\#2\\#3\end{array}\right\}}
\usepackage{amsmath}
\usepackage{mathrsfs}
\newcommand{\e}[1]{\bar{e}_{#1}}
\renewcommand{\r}[1]{\bar{r}_{#1}}
\renewcommand{\deg}{^\circ}
\renewcommand{\vector}[1]{\M{#1}}
\renewcommand{\i}{\vector{i}}
\renewcommand{\j}{\vector{j}}
\renewcommand{\r}{\vector{r}}
\renewcommand{\v}{\vector{v}}
\renewcommand{\a}{\vector{a}}
\pagenumbering{gobble}
\begin{document}
"""

Rab = '^A_B \mathbf{R}'
Rba = '^B_A \\mathbf{R}'
Pa = '^A\mathbf{P}'
Pb = '^B\mathbf{P}'

folder = 'eqns'
if not os.path.exists(folder):
    os.mkdir(folder)

from PIL import Image, ImageOps


def add_background(pathin, pad=10):
    im = Image.open(pathin)
    old_size = im.size  # old_size[0] is in (width, height) format
    new_width = old_size[0] + 2*pad
    new_height = old_size[1] + 2*pad
    new_im = Image.new("RGB", (new_width, new_height), (255,255,255))
    new_im.paste(im, (pad,pad))
    fno, ext = os.path.splitext(pathin)
    pad_path = fno + '_padded.png'
    new_im.save(pad_path)
    return pad_path


def expr_to_png(expr, basename, add_bg=True, pad=10):
    if expr[0] != '$':
        expr = '$' + expr
    if expr[-1] != '$':
        expr += '$'
    curdir = os.getcwd()
    os.chdir(folder)
    fno, ext = os.path.splitext(basename)
    pdf_name1 = fno + '.pdf'
    sympy.preview(expr, viewer='file', output='pdf',filename=pdf_name1,                  preamble=myheader)
    cmd1 = 'pdfcrop_rwk.py %s' % pdf_name1
    os.system(cmd1)
    cropped_pdf_name = fno + '_cropped.pdf'
    cmd2 = 'pdf_to_png_2016.py %s' % cropped_pdf_name
    os.system(cmd2)
    
    if add_bg:
        cropped_png_name = cropped_pdf_name.replace('.pdf','.png')
        add_background(cropped_png_name, pad=pad)
        os.remove(cropped_png_name)
        
    os.chdir(curdir)


def find_eqn_num(basepat='eqn_%i', ext='*.pdf'):
    for i in range(300):
        glob_fn = basepat % i + ext
        glob_pat = os.path.join(folder, glob_fn)
        files = glob.glob(glob_pat)
        if len(files) == 0:
            return i


def save_new(expr, suffix='', base_pat='eqn_%i'):
    new_num = find_eqn_num(base_pat)
    new_base = base_pat % new_num
    new_base += suffix
    expr_to_png(expr, new_base)


def save_num(expr, i, suffix='', base_pat='eqn_%i'):
    new_base = base_pat % i
    new_base += suffix
    expr_to_png(expr, new_base)



def batch_expr_to_png(expr_list, basepat='eqn_%i'):
    for i, expr in enumerate(expr_list):
        curbase = basepat % i
        expr_to_png(expr, curbase)


def tolatex(var):
    outstr = sympy.printing.latex(var)
    #print(outstr)
    return outstr



def rot_mat_dot_prods_one_row(Aletter='X', frameA='A', frameB='B'):
    Bletters = ['X','Y','Z']
    listout = []
    for letter in Bletters:
        cur_ent = '\\hat{%s}_{%s} \\, \\cdot \\, \\hat{%s}_{%s}' % \
                  (letter, frameB, Aletter, frameA)
        listout.append(cur_ent)
    strout = ' & '.join(listout)
    return strout


def rotation_matrix_dot_products(frameA='A',frameB='B'):
    strout = '\\left[ \\begin{matrix} '
    Aletters = ['X','Y','Z']
    for letter in Aletters:
        rowstr = rot_mat_dot_prods_one_row(letter, frameA, frameB)
        strout += rowstr
        if letter != 'Z':
            strout += ' \\\\ '

    strout += ' \\end{matrix} \\right]'
    return strout



def R_BA_R_AB_one_row(Aletter='X', frameA='A', frameB='B'):
    Bletters = ['X','Y','Z']
    listout = []
    for letter in Bletters:
        cur_ent = '^%s\\hat{%s}^T_{%s} \\, \\cdot \\, ^%s\\hat{%s}_{%s}' % \
                  (frameA, Aletter, frameB, frameA, letter, frameB)
        listout.append(cur_ent)
    strout = ' & '.join(listout)
    return strout


def R_BA_R_AB_dot_prod(frameA='A',frameB='B'):
    strout = '\\left[ \\begin{matrix} '
    Aletters = ['X','Y','Z']
    for letter in Aletters:
        rowstr = R_BA_R_AB_one_row(letter, frameA, frameB)
        strout += rowstr
        if letter != 'Z':
            strout += ' \\\\ '

    strout += ' \\end{matrix} \\right]'
    return strout

