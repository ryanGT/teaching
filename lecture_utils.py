import datetime, os, rwkos, sys, copy, rwkmisc, time

firstday = datetime.date(2010, 8, 23)

import pdb
import txt_mixin

from pygimp_lecture_utils import lecturerc_path


rst_line1 = '.. include:: /home/ryan/git/report_generation/header.rst'
rst_title_line = '`\mytitle{@@TITLE@@}`'

rst_list = txt_mixin.txt_list([rst_line1, '', rst_title_line, ''])
#replaceall(self, findpat, rep, forcestart=0):

def date_string_to_datetime(string):
    """Convert a date of the format mm/dd/yy to a datetime object.
    Using spaces or underscores in place of /'s is tolerated."""
    string = string.replace(' ','/')
    string = string.replace('_','/')
    out = time.strptime(string,'%m/%d/%y')
    date = datetime.date(out.tm_year, out.tm_mon, out.tm_mday)
    return date


def find_next_day(today, des_day=0):
    """Find the next Monday or Tuesday or whatever following today.
    des_day is an integer between 0 and 6 where 0 is Monday, 1 is
    Tuesday, ..., and 6 is Sunday."""
    day_delta = des_day - today.weekday()
    delta = datetime.timedelta(days=day_delta, weeks=1)
    return today + delta


def get_valid_date(date=None):
    if date is not None:
        today = date_string_to_datetime(date)
    else:
        today = datetime.date.today()
    if today < firstday:
        return firstday
    else:
        return today

    
class course(object):
    def __init__(self, path):
        self.path = rwkos.FindFullPath(path)


    def format_date(self, date=None, attr='date_str'):
        if date is None:
            if not hasattr(self, 'next_lecture'):
                self.next_lecture_date()
            date = self.next_lecture
        date_str = date.strftime('%m_%d_%y')
        setattr(self, attr, date_str)
        return date_str


    def next_lecture_date(self, date=None):
        raise NotImplementedError

    
    def previous_lecture_date(self, date=None):
        raise NotImplementedError


    def build_lecture_path_string(self, date=None):
        if not hasattr(self, 'date_str'):
            self.format_date(date=date)
        self.lecture_path = os.path.join(self.path, self.date_str)
        return self.lecture_path


    def build_previous_lecture_path(self):
        if not hasattr(self, 'prev_lecture'):
            self.previous_lecture_date()
        self.format_date(date=self.prev_lecture, \
                         attr='prev_date_str')
        self.prev_lecture_path = os.path.join(self.path, \
                                              self.prev_date_str)
        return self.prev_lecture_path



    def make_lecture_dir(self, date=None):
        if not hasattr(self, 'lecture_path'):
            self.build_lecture_path_string(date=date)
        if not os.path.exists(self.lecture_path):
            os.mkdir(self.lecture_path)


    def make_exclude_dir(self):
        self.exclude_path = os.path.join(self.lecture_path, 'exclude')
        if not os.path.exists(self.exclude_path):
            os.mkdir(self.exclude_path)


    def create_one_rst(self, title='Outline'):
        #make this create only if it doens't exist!!!
        rstname = title.lower() + '.rst'
        rstpath = os.path.join(self.exclude_path, rstname)
        if not os.path.exists(rstpath):
            mylist = copy.copy(rst_list)
            mylist.replaceall('@@TITLE@@', title)
            txt_mixin.dump(rstpath, mylist)
        
        
    def create_rsts(self):
        title_list = ['Outline','Announcements','Reminders']
        for title in title_list:
            self.create_one_rst(title)


    def set_pickle(self):
        mydict = {}
        mydict['lecture_path'] = self.lecture_path
        mydict['date_stamp'] = self.next_lecture.strftime('%m/%d/%y')
        mydict['current_slide'] = 0
        self.build_pat()
        mydict['pat'] = self.pat
        mydict['search_pat'] = self.search_pat
        mydict['course_num'] = self.course_num
        rwkmisc.SavePickle(mydict, lecturerc_path)


    def copy_announcements_forward(self, debug=0):
        prev_exclude_path = os.path.join(self.prev_lecture_path, \
                                         'exclude')
        announce_path = os.path.join(prev_exclude_path,
                                     'announcements.rst')
        filein = txt_mixin.txt_file_with_list(announce_path)
        listout = copy.copy(rst_list)
        listout.replaceall('@@TITLE@@', 'Reminders')
        if debug:
            print('pathin = ' + announce_path)
            print('listin = ' + str(filein.list))
        if len(filein.list) > 3:
            listout.extend(filein.list[3:])
        new_exclude_path = os.path.join(self.lecture_path, 'exclude')
        pathout = os.path.join(new_exclude_path, 'reminders.rst')
        if debug:
            print('pathout = ' + pathout)
        txt_mixin.dump(pathout, listout)

        
    def run(self, date=None):
        self.next_lecture_date(date=date)
        self.build_lecture_path_string()
        self.make_lecture_dir()
        self.make_exclude_dir()
        print('lecture_path = ' + self.lecture_path)
        self.build_previous_lecture_path()
        print('previous lecture_path = ' + self.prev_lecture_path)
        self.set_pickle()
        if self.forward:
            self.copy_announcements_forward()
        self.create_rsts()
        
        
class course_458(course):
    def __init__(self, path=None, forward=False):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/mechatronics/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        self.path = rwkos.FindFullPath(path)
        self.course_num = '458'
        self.forward = forward


    def next_lecture_date(self, date=None):
        today = get_valid_date(date=date)
        #458 lectures are on weekdays 0 and 2 (Monday and Wednesday)
        weekday = today.weekday()
        if weekday in [0,2]:
            self.next_lecture = today
        elif weekday == 1:
            self.next_lecture = today + datetime.timedelta(days=1)
        else:
            self.next_lecture = find_next_day(today, \
                                              des_day=0)#find next Monday
        return self.next_lecture


    def previous_lecture_date(self, date=None):
        today = get_valid_date(date=date)
        #458 lectures are on weekdays 0 and 2 (Monday and Wednesday)
        weekday = today.weekday()
        if weekday == 6:#Sunday --> prev. Wed.
            self.prev_lecture = today + datetime.timedelta(days=-4)
        elif weekday == 0:#Monday --> prev. Wed.
            self.prev_lecture = today + datetime.timedelta(days=-5)
        elif weekday in [1,2]:#backup to Mon.
            self.prev_lecture = today + datetime.timedelta(days=-weekday)
        elif weekday == [3,4,5]:#backup to Wed.
            self.prev_lecture = today + datetime.timedelta(days=-weekday+2)
        return self.prev_lecture


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME458_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME458_' + date_pat
        

class course_482(course):
    def __init__(self, path=None, forward=False):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/482/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        self.path = rwkos.FindFullPath(path)
        self.forward = forward
        self.course_num = '482'


    def next_lecture_date(self, date=None):
        today = get_valid_date(date=date)
        #482 lectures are on weekdays 1 and 3 (Tuesday and Thursday)
        weekday = today.weekday()
        if weekday in [1,3]:#Tuesday or Thursday
            self.next_lecture = today
        elif weekday in [0,2]:#Monday or Wednesday
            self.next_lecture = today + datetime.timedelta(days=1)
        else:
            self.next_lecture = find_next_day(today, \
                                              des_day=1)#find next
                                                        #Tuesday
        return self.next_lecture


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME482_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME482_' + date_pat


class course_492(course):
    def __init__(self, path=None, forward=False):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/mobile_robotics/' + \
                   today.strftime('%Y')#4 digit year
            path += '/lectures/'
        self.path = rwkos.FindFullPath(path)
        self.course_num = '492'


    def next_lecture_date(self, date=None):
        today = get_valid_date(date=date)
        #482 lectures are on weekdays 1 and 3 (Tuesday and Thursday)
        weekday = today.weekday()
        if weekday == 2:#Wednesday
            self.next_lecture = today
        elif weekday == 0:#Monday or Wednesday
            self.next_lecture = today + datetime.timedelta(days=2)
        elif weekday == 1:#Monday or Wednesday
            self.next_lecture = today + datetime.timedelta(days=1)
        else:
            self.next_lecture = find_next_day(today, \
                                              des_day=2)#find next
                                                        #Wednesday
        return self.next_lecture


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME492_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME492_' + date_pat
