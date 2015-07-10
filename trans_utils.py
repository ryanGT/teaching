import os, glob, txt_mixin, numpy, shutil, rwkos, re
import banner_parsing
reload(banner_parsing)

import delimited_file_utils

import copy

trans_folder = 'transcripts'

rwkos.make_dir(trans_folder)
html_folder = os.path.join(trans_folder, 'html')
rwkos.make_dir(html_folder)
txt_folder = os.path.join(trans_folder, 'txt')
rwkos.make_dir(txt_folder)

folder_dict = {'.html':html_folder, \
               '.txt':txt_folder}

p_last_first = re.compile('^([A-z]+)-([A-z]+)')

def lastname_and_firstname_from_id(studentid, folder='', ext='.html'):
    filepath = find_trans(studentid=studentid, folder=folder, ext=ext)
    folder, filename = os.path.split(filepath)
    while folder:
        folder, filename = os.path.split(filename)
        
    q = p_last_first.search(filename)
    if q is None:
        from IPython.core.debugger import Pdb
        Pdb().set_trace()
        assert q is not None, "problem with p_last_first and %s" % filepath
    last = q.group(1)
    first = q.group(2)
    if '_' in first:
        first, rest = first.split('_', 1)

    return last, first

    
def lastname_and_firstname_from_row(lastname, firstname=None):
    if (firstname is None) and type(lastname) != str:
        if len(lastname) > 1:
            firstname = lastname[1]
            lastname = lastname[0]
    return lastname, firstname


def make_pat(lastname=None, firstname=None, studentid=None, ext='.html'):
    if studentid:
        glob_pat = '*' + studentid + '*' + ext
    else:
        lastname, firstname = lastname_and_firstname_from_row(lastname, \
                                                              firstname)
        glob_pat = lastname + '*' + firstname + '*' + ext
        
    return glob_pat


def make_pat_folder(lastname=None, firstname=None, studentid=None, \
                    ext='.html', folder=''):
    fn_pat = make_pat(lastname, firstname, studentid=studentid, ext=ext)
    glob_pat = os.path.join(folder, fn_pat)
    return glob_pat


def make_pat_ext_folder(lastname=None, firstname=None, studentid=None, \
                        ext='.html'):
    folder = folder_dict[ext]
    my_pat = make_pat_folder(lastname, firstname, studentid=studentid, \
                             ext=ext, folder=folder)
    return my_pat


def make_pat_html_folder(lastname=None, firstname=None, studentid=None):
    html_pat = make_pat_ext_folder(lastname, firstname, studentid=studentid, \
                                   ext='.html')
    return html_pat


def make_pat_txt_folder(lastname=None, firstname=None, studentid=None):
    txt_pat = make_pat_ext_folder(lastname, firstname, studentid=studentid, \
                                  ext='.txt')
    return txt_pat


def find_trans(lastname=None, firstname=None, studentid=None, \
               ext='.html', folder=''):
    glob_pat = make_pat_folder(lastname, firstname, studentid=studentid, \
                               ext=ext, folder=folder)
    curfiles = glob.glob(glob_pat)
    if len(curfiles) == 1:
        return curfiles[0]
    elif len(curfiles) == 0:
        return None
    else:
        raise ValueError, "found more than one match for %s: %s" % (glob_pat, curfiles)



def find_trans_ext_folder(lastname=None, firstname=None, studentid=None, \
                          ext='.html'):
    folder = folder_dict[ext]
    return find_trans(lastname, firstname, studentid=studentid, \
                      ext=ext, folder=folder)


def find_trans_txt_folder(lastname=None, firstname=None, studentid=None):
    return find_trans_ext_folder(lastname, firstname, studentid=studentid, \
                                 ext='.txt')


def move_trans(lastname=None, firstname=None, studentid=None, ext='.html'):
    dst_folder = folder_dict[ext]
    src_path = find_trans(lastname, firstname, studentid=studentid, \
                          ext=ext, folder='')#find in curdir and move to html folder
    src_folder, fn = os.path.split(src_path)
    dst_path = os.path.join(dst_folder, fn)
    shutil.move(src_path, dst_path)


def pull_trans(lastname=None, firstname=None, studentid=None):
    #cmd = 'transcript.sh ' + id_str
    if studentid is not None:
        studentid = str(studentid)
        use_banner_id = True
    else:
        use_banner_id = False
        lastname, firstname = lastname_and_firstname_from_row(lastname, \
                                                              firstname)


    if use_banner_id:
        cmd = 'transcript.sh %s' % studentid
    else:
        cmd = 'transcript.sh %s %s' % (lastname, firstname)
        
    os.system(cmd)
    move_trans(lastname, firstname, studentid=studentid, \
               ext='.html')


def check_for_trans_html(lastname=None, firstname=None, studentid=None):
    glob_pat = make_pat_html_folder(lastname, firstname, studentid=studentid)
    curfiles = glob.glob(glob_pat)
    if len(curfiles) == 0:
        return False
    elif len(curfiles) == 1:
        return True
    else:
        raise ValueError, "found more than one match for " + glob_pat



