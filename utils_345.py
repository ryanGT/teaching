import pylab_util as PU

import os
from krauss_misc import rwkos, relpath

git_root = os.path.expanduser("~/instructor_git_345/")
images_root = os.path.join(git_root, "345_images")
facweb_images_root = "https://faculty.gvsu.edu/kraussry/345_images"


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


def save_345_image(fn, chapter=2):
    folder = "chapter_%i" % chapter
    folder_path = os.path.join(images_root, folder)
    rwkos.make_dir(folder_path)
    img_path = os.path.join(folder_path, fn)
    PU.mysave(img_path)
    html_str = html_str_to_relpath(img_path)
    return html_str


def find_image_match_list(pat, chapter=None):
    if chapter is not None:
        folder = "chapter_%i" % chapter
        folder_path = os.path.join(images_root, folder)
    else:
        folder_path = images_root

    mylist = rwkos.find_in_top_and_all_sub_dirs(folder_path, pat)
    return mylist


def find_image_345(pat, chapter=None):
    mylist = find_image_match_list(pat, chapter)
    if len(mylist) > 1:
        return mylist
    elif len(mylist) == 1:
        img_path = mylist[0]
        curdir = os.getcwd()
        rp = relpath.relpath(img_path, curdir)
        img_str = '<img src="%s" width=800px>' % rp
        #html_str = html_str_to_relpath(img_path)
        #return html_str
        print(img_str)
    else:
        return None


def find_facweb_image_path(pat, chapter=None):
    """Search for images locally in 445_images.  If more than one image is
    found, return the list.  If exactly one image is found that matches pat,
    convert to html source code assuming the image exists in facweb 445_images.

    Note that I need to manaul sync local 445_images to facweb.  Not attempt 
    is made by this code to verify that the image exists in facweb folder."""
    mylist = find_image_match_list(pat, chapter)
    if len(mylist) > 1:
        return mylist
    else:
        localpath = mylist[0]
        localabs = os.path.abspath(localpath)
        rp = relpath.relpath(localabs, images_root)
        html_path = os.path.join(facweb_images_root, rp)
        html_str = '<img src="%s" width=800px>' % html_path
        return html_str




