import vim
import os

def myfunc():
    vim.current.line = "hello from python"


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

