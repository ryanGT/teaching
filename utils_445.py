import pylab_util as PU

import os
from krauss_misc import rwkos, relpath

git_root = os.path.expanduser("~/instructor_git_445_545/")
images_root = os.path.join(git_root, "445_images")

def save_445_image(fn, chapter=2):
    folder = "chapter_%i" % chapter
    folder_path = os.path.join(images_root, folder)
    rwkos.make_dir(folder_path)
    img_path = os.path.join(folder_path, fn)
    PU.mysave(img_path)
    curdir = os.getcwd()
    rp = relpath.relpath(img_path, curdir)
    rp_fno, ext = os.path.splitext(rp)
    rp_png = rp_fno + '.png'
    html_str = '<img src="%s" width=800px>' % rp_png
    return html_str
