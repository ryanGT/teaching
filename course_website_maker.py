#!/usr/bin/env python
import os, glob, shutil
import thumbnail_maker
reload(thumbnail_maker)

from rst_creator import rst2html_fullpath

from IPython.Debugger import Pdb

class course_website(object):
    def __init__(self, pathin, title, lecture_folders=['lectures'], \
                 other_folders=['homework','labs','projects'], \
                 toplevel_files=['syllabus.pdf'], \
                 extlist=['html','pdf','py','m'], \
                 teaching_root = '../../index.html'):
        #teaching_root assumes that the courses will be in folders by
        #course number and year, i.e. 482/2009 so that the root to all
        #classes is two levels up in ~/siue/classes
        self.pathin = pathin
        self.title = title
        #lecture_folders are folders that need thumbnails made and
        #need to have special treatment for the html of the thumbnails
        #and such.  They can also have pdf, py, m, html, or rst files
        #in them.
        self.lecture_folders = lecture_folders
        #other_folders do not have jper or png lecture slides that
        #need thumbnails made.  They will only be searched
        #for the files in extlist.
        self.other_folders = other_folders
        self.toplevel_files = toplevel_files
        self.extlist = extlist
        self.teaching_root = teaching_root

        

    def make_lecture_pages(self):
        lecture_pages = None
        for folder in self.lecture_folders:
            folder_path = os.path.join(self.pathin, folder)
            title = self.title + ': Lecture Notes'
            lecture_page = thumbnail_maker.MainPageMaker2(folder_path, \
                                                          title=title, \
                                                          DirectoryPageclass=thumbnail_maker.DirectoryPage)
                                                          #DirectoryPageclass=thumbnail_maker.DirectoryPage_courses)
            lecture_page.Go(top_level_link='../index.html')
            if lecture_pages is None:
                lecture_pages = [lecture_page]
            else:
                lecture_pages.append(lecture_page)
        self.lecture_pages = lecture_pages


    def make_other_pages(self):
        other_pages = None
        for folder in self.other_folders:
            folder_path = os.path.join(self.pathin, folder)
            if os.path.exists(folder_path):
                title = self.title + ': ' + folder
                other_page = thumbnail_maker.MainPageMaker_no_images(folder_path, \
                                                                     title=title, \
                                                                     DirectoryPageclass=thumbnail_maker.DirectoryPage_no_images)
                other_page.Go(top_level_link='../index.html')
                if other_pages is None:
                    other_pages = [other_page]
                else:
                    other_pages.append(other_page)
        self.other_pages = other_pages

    
    def make_toplevel_page(self):
        pat = os.path.join(self.pathin, 'index_*.rst')
        myfiles = glob.glob(pat)
        if len(myfiles) == 1:
            src = myfiles[0]
            dst = os.path.join(self.pathin, 'index.rst')
            shutil.copyfile(src, dst)
            rst2html_fullpath(dst)
            

    def go(self):
        self.make_lecture_pages()
        self.make_other_pages()
        self.make_toplevel_page()

        
if __name__ == '__main__':
    mypath = '/home/ryan/siue/classes/450/2010/'
    my_course_page = course_website(mypath, \
                                    'ME 450', \
                                    other_folders=['python_install',\
                                                   #'homework',\
                                                   #'labs',\
                                                   #'projects',\
                                                   #'python_tutorial',\
                                                   ]\
                                    )
    #my_course_page.go()
    #Pdb().set_trace()
    my_course_page.make_other_pages()

##     path2 = '/home/ryan/siue/classes/484/2010'
##     course2 = course_website(path2, 'ME 484')
##     course2.go()
    
