import os, glob, shutil, copy
from krauss_misc import relpath, txt_mixin, rwkos

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
        #skipfolders = ['.ipynb_checkpoints','figs','prep','solutions']
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



class student_file_finder_filter_older(student_file_finder):
    """This class checks to see if a file is newer than another file
    with a different extension but the same filename (fno), and
    filters out files that are older than the other extension.  One
    example usecase is gdoc-down: downloading a pdf from google drive
    is somewhat time consuming, so only do it if the gdoc or gslides
    file is newer than the pdf.

    return True if the test fails and filename should not be copied
    (because it is older than the pdf or whatever)."""
    def __init__(self, topdir, preferred_root, bad_root=None, ext_list=default_ext_list, \
                 check_ext='.pdf'):
        student_file_finder.__init__(self, topdir, preferred_root, \
                                     bad_root=bad_root, ext_list=ext_list) 
        self.check_ext = check_ext

        
    def filter_older(self, filename):
        fno, ext = os.path.splitext(filename)
        checkname = fno + self.check_ext
        if os.path.exists(checkname):
            chkmtime = os.path.getmtime(checkname)
            docmtime = os.path.getmtime(filename)
            if docmtime > chkmtime:
                return False
            else:
                return True
        else:
            return False
    


    def main(self, filter_older=True):
        allpaths = student_file_finder.main(self)
        if filter_older:
            filt_paths = []
            for curpath in allpaths:
                if not self.filter_older(curpath):
                    filt_paths.append(curpath)
            self.allpaths = filt_paths
        return self.allpaths



gdoc_down_ext_list = ['.gdoc','.gslides']


class student_file_finder_gdoc_down(student_file_finder_filter_older):
    def __init__(self, topdir, preferred_root, bad_root=None, ext_list=gdoc_down_ext_list, \
                 check_ext='.pdf'):
        student_file_finder_filter_older.__init__(self, topdir, preferred_root, \
                                                  bad_root=bad_root, ext_list=ext_list, \
                                                  check_ext=check_ext)


class student_file_finder_pdf_only(student_file_finder):
    def __init__(self, topdir, preferred_root, bad_root=None, ext_list=['.pdf']):
        student_file_finder_filter_older.__init__(self, topdir, preferred_root, \
                                                  bad_root=bad_root, ext_list=ext_list)


class student_file_finder_nbs(student_file_finder_filter_older):
    def __init__(self, topdir, preferred_root, bad_root=None, ext_list=['.ipynb']):
        student_file_finder_filter_older.__init__(self, topdir, preferred_root, \
                                                  bad_root=bad_root, ext_list=ext_list)


    def main(self, filter_older=True):
        allpaths = student_file_finder.main(self)
        rawpaths = copy.copy(allpaths)
        filtpaths = [nb for nb in rawpaths if "_for_students" not in nb]
        allpaths = filtpaths
        self.allpaths = allpaths
        if filter_older:
            filt_paths = []
            for curpath in allpaths:
                if not self.filter_older(curpath):
                    filt_paths.append(curpath)
            self.allpaths = filt_paths
        return self.allpaths



    def filter_older(self, filename):
        fno, ext = os.path.splitext(filename)
        checkname = fno + "_for_students.ipynb"
        if os.path.exists(checkname):
            chkmtime = os.path.getmtime(checkname)
            docmtime = os.path.getmtime(filename)
            if docmtime > chkmtime:
                return False
            else:
                return True
        else:
            return False


class folder_processor_gdoc_jupyter_pdf(object):
    def __init__(self, topdir, preferred_root, dst_path, bad_root=None):
        self.topdir = topdir
        self.preferred_root = preferred_root
        self.bad_root = bad_root
        self.dst_path = dst_path
        self.gdoc_finder =  student_file_finder_gdoc_down(self.topdir, \
                                                          self.preferred_root, \
                                                          bad_root=self.bad_root)
        self.pdf_finder = student_file_finder_pdf_only(self.topdir,
                                                       self.preferred_root, \
                                                       bad_root=self.bad_root)
        self.nb_finder = student_file_finder_nbs(self.topdir,
                                                 self.preferred_root, \
                                                 bad_root=self.bad_root)

    def gdoc_down(self):
        curdir = os.getcwd()
        os.chdir(self.topdir)
        for filename in self.gdoc_finder.allpaths:
            cmd = "gdoc-down -f pdf %s" % filename
            print(cmd)
            os.system(cmd)
        os.chdir(curdir)

        
    def copy_files(self, filenames, verbosity=1):
        curdir = os.getcwd()
        os.chdir(self.topdir)
        for filename in filenames:
            src1 = os.path.join(self.topdir, filename)
            dst1 = os.path.join(self.dst_path, filename)
            if verbosity > 0.5:
                print("src = %s" % src1)
                print("dst = %s" % dst1)
            shutil.copyfile(src1, dst1)
        os.chdir(curdir)


    def copy_pdfs(self):
        self.copy_files(self.pdf_finder.allpaths)


    def main(self):
        """- make dst folder if necessary (check)
           - find and process new or updated google docs (check)
           - find and process jupyter notebooks (TBD)
           - find and copy pdfs"""
        rwkos.make_dir(self.dst_path)
        self.gdoc_finder.main()
        self.gdoc_down()
        self.nb_finder.main()
        self.pdf_finder.main()
        self.copy_pdfs()



class folder_processor_jupyter_to_pdf_doc(folder_processor_gdoc_jupyter_pdf):
    def convert_nbs_to_pdf_docs(self):
        curdir = os.getcwd()
        os.chdir(self.topdir)
        for filename in self.nb_finder.allpaths:
            cmd = "jupyter_notebook_to_pdf.py %s" % filename
            os.system(cmd)
        os.chdir(curdir)


    def clean_up_md_convert(self):
        curdir = os.getcwd()
        os.chdir(self.topdir)
        pat_list = ["*_for_pdf.*", "*_out.*"]
        for pat in pat_list:
            matches = glob.glob(pat)
            for match in matches:
                os.remove(match)
        os.chdir(curdir)
        
        
    def main(self):
        """- make dst folder if necessary (check)
            - find and process new or updated google docs (check)
            - find and process jupyter notebooks (TBD)
            - find and copy pdfs"""
        rwkos.make_dir(self.dst_path)
        self.gdoc_finder.main()
        self.gdoc_down()
        self.nb_finder.main()
        self.convert_nbs_to_pdf_docs()
        self.clean_up_md_convert()
        self.pdf_finder.main()
        self.copy_pdfs()
    



class folder_processor_jupyter_to_pdf_copy_both(folder_processor_jupyter_to_pdf_doc):
    def make_student_nbs(self):
        curdir = os.getcwd()
        os.chdir(self.topdir)
        for filename in self.nb_finder.allpaths:
            cmd = "jupyter_notebook_auto_gen_starter_student_notebook.py %s" % filename
            os.system(cmd)

        self.student_nbs = glob.glob("*_for_students.ipynb")


    def copy_student_nbs(self):
        # distributing notebooks with local image paths that won't work for
        # anyone else seems like a bad idea
        self.copy_files(self.student_nbs)
        

    def main(self):
        """- make dst folder if necessary (check)
            - find and process new or updated google docs (check)
            - find and process jupyter notebooks (TBD)
            - find and copy pdfs"""
        rwkos.make_dir(self.dst_path)
        self.gdoc_finder.main()
        self.gdoc_down()
        self.nb_finder.main()
        self.convert_nbs_to_pdf_docs()
        self.make_student_nbs()
        self.copy_student_nbs()
        self.clean_up_md_convert()
        self.pdf_finder.main()
        self.copy_pdfs()



class folder_processor_copy_jupyter_and_pdf_no_processing(folder_processor_jupyter_to_pdf_copy_both):
    """This class assume jupyter notebooks have already been processed and simply
    copies pdf and ipynb files."""
    def copy_nbs(self):
        self.copy_files(self.nb_finder.allpaths)


    def main(self):
        """- make dst folder if necessary (check)
        - find and process new or updated google docs (check)
        - find and process jupyter notebooks (TBD)
        - find and copy pdfs"""
        rwkos.make_dir(self.dst_path)
        self.gdoc_finder.main()
        self.gdoc_down()
        self.nb_finder.main()
        self.copy_nbs()
        self.clean_up_md_convert()
        self.pdf_finder.main()
        self.copy_pdfs()

