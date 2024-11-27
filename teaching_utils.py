import os, glob


def find_cp_folder(i, cpdir):
    name_pat = "class_%0.2i" % i
    pat2 = name_pat + '*'
    fullpat = os.path.join(cpdir, pat2)
    all_folders = glob.glob(fullpat)
    if len(all_folders) == 0:
        return False
    else:
        return all_folders[0]


def find_at_least_one_match(i, cpdir):
    myfolder = find_cp_folder(i, cpdir)
    if myfolder:
        return True
    # if not found:
    return False



def get_highest_class_number(cpdir):
    """Search in cpdir to find the highest numbered match 
    to class_%02i*"""
    for i in range(1,200):
        found = find_at_least_one_match(i,cpdir)
        if not found:
            classnum = i-1
            return classnum


def find_one_slides_file(mydir):
    fnpat = "*_slides.md"
    fullpat = os.path.join(mydir, fnpat)
    all_matches = glob.glob(fullpat)
    if len(all_matches) == 1:
        return all_matches[0]
    
