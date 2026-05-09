import pylab_util as PU

import os
from krauss_misc import rwkos, relpath

git_root = os.path.expanduser("~/instructor_git_445_545/")
images_root = os.path.join(git_root, "445_images")


def html_str_to_relpath(img_path):
    curdir = os.getcwd()
    rp = relpath.relpath(img_path, curdir)
    rp_fno, ext = os.path.splitext(rp)
    ## Hard coding png is bad
    ## - find png or jpg or jpeg if they exist
    ## - relative path should exist from here
    if ext == ".pdf":
        img_found = False
        myexts = ['.png', '.jpg','.jpeg']
        for test_ext in myexts:
            test_img_rp = rp_fno + test_ext
            if os.path.exists(test_img_rp):
                rp_img = test_img_rp
                img_round = True
                break
    else:
        ## if it is not a pdf, assume it is an image
        rp_img = rp
    #rp_png = rp_fno + '.png'
    html_str = '<img src="%s" width=800px>' % rp_img
    return html_str


def save_445_image(fn, chapter=2):
    folder = "chapter_%i" % chapter
    folder_path = os.path.join(images_root, folder)
    rwkos.make_dir(folder_path)
    img_path = os.path.join(folder_path, fn)
    PU.mysave(img_path)
    html_str = html_str_to_relpath(img_path)
    return html_str


def find_image_445(pat, chapter=None):
    if chapter is not None:
        folder = "chapter_%i" % chapter
        folder_path = os.path.join(images_root, folder)
    else:
        folder_path = images_root

    mylist = rwkos.find_in_top_and_all_sub_dirs(folder_path, pat)
    if len(mylist) > 1:
        return mylist
    elif len(mylist) == 1:
        img_path = mylist[0]
        html_str = html_str_to_relpath(img_path)
        return html_str
    else:
        return None



