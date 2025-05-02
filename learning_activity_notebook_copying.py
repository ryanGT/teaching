#!/usr/bin/env python3
"""This module exists to help copy jupyter notebooks back and
forh between solution repositories and student repositories.

This module is used by other scripts that do more detailed work,
like removing solutions from notebooks heading to student
repositories"""
import os, shutil, re, shutil
from krauss_misc import rwkos
from krauss_misc import relpath


student_folders = ['/Users/kraussry/445_local_prep/learning_activities_EGR_445_545']
solution_folders = ['/Users/kraussry/445_local_prep/solutions_EGR_445_545']
mymap = dict(zip(solution_folders, student_folders))
inv_map = {v: k for k, v in mymap.items()}


def am_I_in_solution_folder(curdir):
    for key, value in mymap.items():
        if key in curdir:
            return True



def am_I_in_student_folder(curdir):
    for key, value in inv_map.items():
        if key in curdir:
            return True



def get_src_and_dst_roots(curdir):
    mydict = None
    if am_I_in_solution_folder(curdir):
        mydict = mymap
    elif am_I_in_student_folder(curdir):
        mydict = inv_map

    assert mydict is not None, "we are not in a student or solution folder"

    for key, value in mydict.items():
        print("key: %s" % key)
        if key in curdir:
            src_root = key
            dst_root = value
            return src_root, dst_root


def copy_common_foundations(src_path):
    src_root, dst_root = get_src_and_dst_roots(src_path)
    rest, nb_in_name = os.path.split(src_path)
    folder_rel_path = relpath.relpath(rest, src_root)
    folder_dst_path = os.path.join(dst_root, folder_rel_path) 
    rwkos.make_dirs_recrusive(folder_dst_path)
    return folder_dst_path



def copy_to_solutions_folder(src_path):
    assert am_I_in_student_folder(src_path), \
            "src_path not in a student folder:%s" % src_path
    folder_dst_path = copy_common_foundations(src_path) 
    rest, nb_in_name = os.path.split(src_path)
    fno, ext = os.path.splitext(nb_in_name)
    out_name = fno + "_solution" + ext
    nb_dst_path = os.path.join(folder_dst_path, out_name)
    shutil.copyfile(src_path, nb_dst_path)


def copy_to_student_folder(src_path):
    assert am_I_in_solution_folder(src_path), \
            "src_path not in a solution folder:%s" % src_path
    folder_dst_path = copy_common_foundations(src_path)
    rest, nb_in_name = os.path.split(src_path)
    fno, ext = os.path.splitext(nb_in_name)

    fno = re.sub("_solution$", "", fno)#remove _solution from end of filename
    out_name = fno + ext
    nb_dst_path = os.path.join(folder_dst_path, out_name)
    shutil.copyfile(src_path, nb_dst_path)


