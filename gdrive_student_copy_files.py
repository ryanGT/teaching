import os, glob, shutil, relpath, txt_mixin, rwkos

default_ext_list = ['.pdf','.ipynb','.jpg','.png','.jpeg','.txt']

class student_file_finder(object):
    """This class exists to help find the files that should be copied from
    an instructor or prep google drive folder to one intended for student use.

    Some folders will be skipped (see self.skipfolder) and only some
    extensions will be copied, based on ext_list.

    I have had issues in the past with symbolic links or other things
    causing weird relative paths.  So, bad_root is a base path that
    should be replaced with preferred_root."""
    def __init__(self, topdir, preferred_root, bad_root=None, ext_list=default_ext_list):
        self.topdir = topdir
        self.preferred_root = preferred_root
        self.bad_root = bad_root
        self.ext_list = ext_list


    def skipfolder(self, folderpath):
        """Determing if folder should be autoskipped"""
        skipfolders = ['.ipynb_checkpoints','figs','prep','solutions','eqns','tikz_slides', \
                       'instructor_resources']
        rest, folder = os.path.split(folderpath)
        mytest = rest == folderpath

        if (folder[0] == '.') or (folder in skipfolders) or ("scans" in folder):
            return True


    def main(self):
        allpaths = []

        if self.bad_root in self.topdir:
            self.topdir = self.topdir.replace(self.bad_root, self.preferred_root)

        for root, dirs, files in os.walk(self.topdir):
            #print("root = %s" % root)
            curpaths = self.process_one_folder(root)
            allpaths.extend(curpaths)

        self.allpaths = allpaths
        return allpaths


    def process_one_folder(self, folderpath):
        mypaths = []
        
        if not self.skipfolder(folderpath):
            rp = relpath.relpath(folderpath, self.preferred_root)
            #print("rp = %s" % rp)

            rwkos.clean_files_in_folder(folderpath)

            #ext_list = ['.pdf','.ipynb','.gslides','.gdoc','.jpg','.png','.jpeg']


            for ext in self.ext_list:
                if ext[0] != '*':
                    ext = '*' + ext
                pat = os.path.join(folderpath, ext)
                files = glob.glob(pat)
                rplist = [relpath.relpath(item, self.topdir) for item in files]
                mypaths.extend(rplist)

        return mypaths

        
ext_list_185 = ['.pdf','.jpg','.png','.jpeg','.txt']
        
class student_file_finder_185(student_file_finder):
    def __init__(self, topdir, preferred_root, bad_root=None, ext_list=ext_list_185):
        student_file_finder.__init__(self, topdir, preferred_root, \
                                     bad_root=bad_root, ext_list=ext_list) 
