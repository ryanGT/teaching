import vim
import os
#import tkinter
#import tkinter as tk
#from tkinter import ttk
#import tkinter.filedialog
#from krauss_misc import relpath

def myfunc():
    vim.current.line = "hello from python"


def insert_cols():
    myrange = vim.current.range
    ind = myrange.start	
    mybuf = vim.current.buffer
    mylist = ["\\vspace{-0.2in}", \
              "\\columnsbegin", \
              "\\column{.5\\textwidth}", \
              "", \
              "", \
              "\\column{.5\\textwidth}", \
              "", \
              "", \
              "", \
              "\\columnsend", \
              ""]
    mybuf.append(mylist, ind)


def insert_string(mystr):
    myrange = vim.current.range
    ind = myrange.start	
    mybuf = vim.current.buffer
    mybuf.append(mystr, ind)


def insert_image():
    fullpath = vim.current.buffer.name
    curdir, filename = os.path.split(fullpath)
    fname = None
    if fname:
        rp = relpath.relpath(fname, curdir)
        print("rp = %s" % rp)
        figline = '\\myvfig{0.8\\textheight}{%s}' % rp
        insert_string(figline)


def build_pres():
    fullpath = vim.current.buffer.name
    folder, filename = os.path.split(fullpath)
    os.chdir(folder)
    cmd = "md_to_beamer_pres.py %s" % filename
    os.system(cmd)


def open_pres_skim():
    fullpath = vim.current.buffer.name
    folder, filename = os.path.split(fullpath)
    os.chdir(folder)
    pdf_name = filename.replace("_slides.md", '_main.pdf')
    cmd = "skim %s &" % pdf_name
    os.system(cmd)

