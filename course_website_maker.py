import os
import thumbnail_maker
reload(thumbnail_maker)


class course_website(object):
    def __init__(self, pathin, title, lecture_folders=['lectures'], \
                 other_folders=['homework','labs','projects'], \
                 toplevel_files=['syllabus.pdf'], \
                 extlist=['rst','html','pdf','py','m'], \
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
                                                          title=title)
            lecture_page.Go()
            if lecture_pages is None:
                lecture_pages = [lecture_page]
            else:
                lecture_pages.append(lecture_page)
        self.lecture_pages = lecture_pages


    def make_other_pages(self):
        pass
    
