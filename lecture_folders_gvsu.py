import os, shutil, pdb, glob, re
from krauss_misc import rwkos

#lecture_pat = re.compile("^lecture_([0-9]+)_")
lecture_pat = re.compile("^class_([0-9]+)_")

def find_next_lecture_num(root):
    """Search through the folder whose names match lecture_##_ and
    then find the highest existing number.  Return that number +1."""
    glob_path = os.path.join(root, "class_*")
    folders = glob.glob(glob_path)
    folders.sort()
    
    lect_nums = []

    for folder_path in folders:
        rest, folder = os.path.split(folder_path)
        q = lecture_pat.search(folder)
        if q:
            cur_num = int(q.group(1))
            lect_nums.append(cur_num)

    if lect_nums:
        lect_nums.sort()
        return lect_nums[-1] + 1

    else:
        return 1
    

def build_lecture_path(root, title, lecture_num):
    basename = rwkos.clean_fno_or_folder(title)# assumes title never
                                               # contains an extension,
                                               # which would be really weird
                                               # anyways
    foldername = 'class_%0.2i_%s' % (lecture_num, basename)
    folderpath = os.path.join(root, foldername)
    return folderpath


def find_lecture_number(root, title):
    basename = rwkos.clean_fno_or_folder(title)
    glob_pattern = "class_*_%s*" % basename
    glob_path = os.path.join(root,glob_pattern)
    matches = glob.glob(glob_path)
    if not matches:
        return -1
    else:
        assert len(matches) == 1, "found more than one match for %s" % basename
        folder_path = matches[0]
        rest, folder = os.path.split(folder_path)
        q = lecture_pat.search(folder)
        if q:
            return int(q.group(1))
        else:
            return -1
        

def create_lecture_folder(root, title, lecture_num):
    folderpath = build_lecture_path(root, title, lecture_num)
    rwkos.make_dir(folderpath)
    return folderpath
