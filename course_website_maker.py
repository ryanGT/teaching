#!/usr/bin/env python
import os, glob, shutil, pdb
import thumbnail_maker
reload(thumbnail_maker)

from rst_creator import rst2html_fullpath

#from IPython.core.debugger import Pdb

class course_website(object):
    def __init__(self, pathin, title, lecture_folders=['lectures'], \
                 other_folders=['homework','labs'], \
                 index_rst_only_folders=['projects'], \
                 toplevel_files=['syllabus.pdf'], \
                 extlist=['html','pdf','py','m','txt'], \
                 teaching_root = '../../index.html', \
                 skiplist=[]):
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
        self.index_rst_only_folders = index_rst_only_folders
        self.toplevel_files = toplevel_files
        self.extlist = extlist
        self.teaching_root = teaching_root
        self.skiplist = skiplist


    def make_lecture_pages(self):
        lecture_pages = None

        for folder in self.lecture_folders:
            print('folder='+folder)
            folder_path = os.path.join(self.pathin, folder)
            title = self.title + ': Lecture Notes'
            lecture_page = thumbnail_maker.MainPageMaker2(folder_path, \
                                                          title=title, \
                                                          DirectoryPageclass=thumbnail_maker.DirectoryPage, \
                                                          extlist=self.extlist, \
                                                          skiplist=self.skiplist)
                                                          #DirectoryPageclass=thumbnail_maker.DirectoryPage_courses)
            #pdb.set_trace()
            lecture_page.Go(top_level_link='../index.html')
            if lecture_pages is None:
                lecture_pages = [lecture_page]
            else:
                lecture_pages.append(lecture_page)
        self.lecture_pages = lecture_pages

    def _make_other_pages(self, folders, directorypageclass):
        pages = None
        for folder in folders:
            folder_path = os.path.join(self.pathin, folder)
            if os.path.exists(folder_path):
                title = self.title + ': ' + folder
                myclass = thumbnail_maker.MainPageMaker_no_images
                page = myclass(folder_path, \
                               title=title, \
                               DirectoryPageclass=directorypageclass, \
                               extlist=self.extlist)
                page.Go(top_level_link='../index.html')
                if pages is None:
                    pages = [page]
                else:
                    pages.append(page)
        return pages


    def make_other_pages(self):
        other_pages = self._make_other_pages(self.other_folders, \
                                             thumbnail_maker.DirectoryPage_no_images)
        self.other_pages = other_pages


    def make_index_rst_only_pages(self):
        index_only_pages = self._make_other_pages(self.index_rst_only_folders, \
                                                  thumbnail_maker.DirectoryPage_index_rst_only)
        self.index_only_pages = index_only_pages


    def run_top_level_rst(self, add_back_link=True):
        pat = os.path.join(self.pathin, '*.rst')
        top_level_rst = glob.glob(pat)
        for curpath in top_level_rst:
            folder, name = os.path.split(curpath)
            if name != 'index.rst':
                rst2html_fullpath(curpath, add_up_link=add_back_link, \
                                  uplink_path='index.html')



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
        self.make_index_rst_only_pages()
        self.run_top_level_rst()

class research_website(course_website):
    def __init__(self, pathin, title, \
                 other_folders=[], \
                 index_rst_only_folders=[], \
                 toplevel_files=[], \
                 extlist=['html','pdf','py','m','txt','zip'], \
                 teaching_root = '../../index.html'):
        course_website.__init__(self, pathin, title, \
                                lecture_folders=[], \
                                other_folders=other_folders, \
                                index_rst_only_folders=index_rst_only_folders, \
                                toplevel_files=toplevel_files, \
                                extlist=extlist, \
                                teaching_root=teaching_root)

    def go(self):
        #self.make_lecture_pages()
        self.make_other_pages()
        self.make_toplevel_page()
        self.make_index_rst_only_pages()
        self.run_top_level_rst()


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

