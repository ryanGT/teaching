import datetime, os, rwkos, sys, copy, rwkmisc, time, rst_creator, \
       rst_utils, shutil, pdb, glob

reload(rst_utils)

#firstday = datetime.date(2010, 8, 23)
#firstday = datetime.date(2011, 1, 10)
#firstday = datetime.date(2011, 5, 23)
#firstday = datetime.date(2012, 1, 9)
#firstday = datetime.date(2013, 1, 7)
#firstday = datetime.date(2013, 5, 20)
firstday = datetime.date(2015, 8, 24)

import pdb
import txt_mixin

#from IPython.core.debugger import Pdb

#from pygimp_lecture_utils import lecturerc_path
from pygimp_lecture_pickle_path import lecturerc_path


home_dir = os.path.expanduser('~')
lecture_outline_css_path = rwkos.FindFullPath('git/report_generation/lecture_outline.css')

#rst_line1 = '.. include:: %s/git/report_generation/beamer_header.rst' % home_dir
#rst_title_line = '`\mytitle{@@TITLE@@}`'

#rst_list = txt_mixin.txt_list([rst_line1, '', rst_title_line, ''])
rst_list = txt_mixin.txt_list([])
#replaceall(self, findpat, rep, forcestart=0):


def list_pdfs_find_handout(pdf_files):
    """Given a list of pdfs from a glob search of a directory, find
    the _handout.pdf file and remove it corresponding non-handout file
    if found.  Return the handout file name and the rest of the pdf
    files."""
    pdflist = txt_mixin.txt_list(pdf_files)
    handout_pat = '_handout.pdf'
    handoutinds = pdflist.findall(handout_pat)

    if len(handoutinds) == 1:
        handoutfile = pdflist[handoutinds[0]]
        non_handout_name = handoutfile.replace('_handout','')
        non_handout_inds = pdflist.findall(non_handout_name)
        if len(non_handout_inds) == 1:
            pdflist.pop(non_handout_inds[0])

        handout_name = handoutfile
        listout = []
        # pop the handoutfile from the original list
        handoutind = pdflist.find(handoutfile)
        pdflist.pop(handoutind)
        listout.extend(pdflist)
    else:
        handout_name = None
        listout = pdflist
        
    return handout_name, listout



def list_lecture_files(root_dir, other_exts=['*.py','*.m','*.csv','*.txt']):
    """Make list of relevant files to copy from a lecture prep source
    dir to the actual lecture date dir for the website."""
    def myglob(ext):
        """glob in root dir"""
        if '.' not in ext:
            ext = '.' + ext
        if '*' not in ext:
            ext = '*' + ext
        pat  = os.path.join(root_dir, ext)
        filelist = glob.glob(pat)
        return filelist
    
    pdflist = myglob('*.pdf')
    handout_name, other_pdfs = list_pdfs_find_handout(pdflist)
    if handout_name is not None:
        all_pdfs = [handout_name] + other_pdfs
    else:
        all_pdfs = other_pdfs

    all_items = all_pdfs

    for ext in other_exts:
        curfiles = myglob(ext)
        if curfiles:
            all_items.extend(curfiles)

    return all_items


    
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


def get_valid_date(date=None, force_next=False):
    if date is not None:
        today = date_string_to_datetime(date)
    else:
        today = datetime.date.today()
    if today < firstday:
        return firstday
    else:
        if force_next:
            today += datetime.timedelta(days=1)
        return today


class course(object):
    def __init__(self, path):
        rwkos.make_dirs_recrusive(path)
        self.path = rwkos.FindFullPath(path)
        assert self.path, "Problem with finding/creating path: %s" % path
        rwkos.make_dir(self.path)


    def format_date(self, date=None, attr='date_str'):
        if date is None:
            if not hasattr(self, 'next_lecture'):
                self.next_lecture_date()
            date = self.next_lecture
        date_str = date.strftime('%m_%d_%y')
        print('date_str = ' + date_str)
        setattr(self, attr, date_str)
        return date_str


    def next_lecture_date(self, date=None, force_next=False):
        raise NotImplementedError


    def previous_lecture_date(self, date=None, force_next=False):
        raise NotImplementedError


    def build_lecture_path_string(self, date=None):
        if (date is not None) or (not hasattr(self, 'date_str')):
            self.format_date(date=date)
        self.lecture_path = os.path.join(self.path, self.date_str)
        return self.lecture_path


    def build_previous_lecture_path(self, date=None, force_next=False):
        if not hasattr(self, 'prev_lecture'):
            self.previous_lecture_date(date=date, force_next=force_next)
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

    def course_number_stamp(self):
        cn = str(self.course_num)
        if cn == '106':
            cn_str = 'IE ' + cn
        else:
            cn_str = 'ME ' + cn
        self.cn_str = cn_str
        return self.cn_str
    

    def date_stamp(self):
        self.date_stamp = self.next_lecture.strftime('%m/%d/%y')
        print('date_stamp = ' + self.date_stamp)
        return self.date_stamp

    def course_date_stamp(self):
        date_stamp = self.date_stamp()
        cn = self.course_number_stamp()
        stamp = '%s; %s' % (date_stamp, cn)
        self.stamp = stamp
        return self.stamp


    def create_date_stamp_logo(self):
        dsl_lines = ['.. raw:: latex', \
                     '']

        def out(line, level=1):
            ws = '    '
            dsl_lines.append(ws*level + line)
        out('\\logo{%')
        out('\\makebox[\\paperwidth]{%', level=2)
        cn = str(self.course_num)
        if cn == '106':
            cn_str = 'IE ' + cn
        else:
            cn_str = 'ME ' + cn
        date_str = self.next_lecture.strftime('%m/%d/%y')
        print('date_str = ' + date_str)
        date_line = '\\hspace{7pt}{\\footnotesize %s; %s}' % (cn_str, date_str)
        out(date_line, level=3)
        out('\\hfill%', level=3)
        out('}%', level=2)
        out('}')
        dsl_lines.append('')#blank line with no white space
        return dsl_lines


    def create_date_stamp_section(self):
        """Put date stamp in section rather than logo."""
        dss_lines = []
        out = dss_lines.append
        ## out('dummy')
        ## out('++++++++++++')
        ## out('')
        ## out('dummy')
        ## out('~~~~~~~~~~~~~~')
        ## out('')
        
        cn = str(self.course_num)
        if cn == '106':
            cn_str = 'IE ' + cn
        else:
            cn_str = 'ME ' + cn
        date_str = self.next_lecture.strftime('%m/%d/%y')

        stamp_line = '%s; %s' % (cn_str, date_str)
        out(stamp_line)
        out('-----------------------------------------------------------')
        return dss_lines
    

    def create_rst2gimp_rst(self, force=0):
        rstname = 'outline.rst'
        rstpath = os.path.join(self.exclude_path, rstname)
        if not os.path.exists(rstpath) or force:
            mylist = ['']
            mydec = rst_creator.rst_section_level_2()
            #date_stamp = self.create_date_stamp_logo()
            date_stamp = self.create_date_stamp_section()
            mylist.extend(date_stamp)
            sections = ['Outline', 'Announcements', 'Reminders']
            for section in sections:
                mylist.append('')
                mylist.extend(mydec(section))
                mylist.append('')
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
        mydict['outline_slide'] = 0
        self.build_pat()
        mydict['pat'] = self.pat
        mydict['search_pat'] = self.search_pat
        mydict['course_num'] = self.course_num
        mydict['png_name'] = ''#used for auto png loading or filename suggesting
        mydict['outline_pat'] = 'outline_%0.4i.png'
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


    def copy_announcements_rst2gimp(self, debug=0):
        if not hasattr(self, 'prev_lecture_path'):
            print('not copying previous lecture stuff')
            return
        prev_exclude_path = os.path.join(self.prev_lecture_path, \
                                         'exclude')
        prev_outline_path = os.path.join(prev_exclude_path,
                                         'outline.rst')
        prev_filein = rst_utils.rst_file(prev_outline_path)
        cur_outline_path = os.path.join(self.exclude_path, 'outline.rst')
        cur_rst = rst_utils.rst_file(cur_outline_path)
        prev_ann_list = prev_filein.get_section_contents('Announcements')
        if prev_ann_list is not None:
            list2 = [item.strip() for item in prev_ann_list]
            filt_list = filter(None, list2)
            if filt_list:
                cur_rst.replace_section('Reminders', prev_ann_list)
        txt_mixin.dump(cur_outline_path, cur_rst.list)


    def copy_prev_outline(self):
        prev_exclude_path = os.path.join(self.prev_lecture_path, 'exclude')
        prev_outline_path = os.path.join(prev_exclude_path, 'outline.rst')
        copy_outline_path = os.path.join(self.exclude_path, 'prev_outline.rst')
        if os.path.exists(prev_outline_path):
            shutil.copy(prev_outline_path, copy_outline_path)
        else:
            print('did not find previous outline: '+prev_outline_path)


    def run(self, date=None, build_previous=True, force_next=False):
        self.next_lecture_date(date=date, force_next=force_next)
        self.build_lecture_path_string()
        self.make_lecture_dir()
        self.make_exclude_dir()
        print('lecture_path = ' + self.lecture_path)
        #copy css for rst2html outline
        shutil.copy2(lecture_outline_css_path,self.exclude_path)
        if build_previous:
            self.build_previous_lecture_path(date=date, force_next=force_next)
            print('previous lecture_path = ' + self.prev_lecture_path)
            self.copy_prev_outline()
        self.set_pickle()
        self.create_rst2gimp_rst()
        if self.forward:
            #self.copy_announcements_forward()
            self.copy_announcements_rst2gimp()
        #self.create_rsts()



class course_458(course):
    def __init__(self, path=None, forward=False):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/Fall_2015/458_Fall_2015'
            path += '/lectures/'
        course.__init__(self, path)
        ## self.path = rwkos.FindFullPath(path)
        ## rwkos.make_dir(self.path)
        self.course_num = '458'
        self.forward = forward


    def next_lecture_date(self, date=None, force_next=False):
        today = get_valid_date(date=date, force_next=force_next)
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


    def previous_lecture_date(self, date=None, force_next=False):
        today = get_valid_date(date=date, force_next=force_next)
        #458 lectures are on weekdays 0 and 2 (Monday and Wednesday)
        weekday = today.weekday()
        if weekday == 6:#Sunday --> prev. Wed.
            self.prev_lecture = today + datetime.timedelta(days=-4)
        elif weekday == 0:#Monday --> prev. Wed.
            self.prev_lecture = today + datetime.timedelta(days=-5)
        elif weekday in [1,2]:#backup to Mon.
            self.prev_lecture = today + datetime.timedelta(days=-weekday)
        elif weekday in [3,4,5]:#backup to Wed.
            self.prev_lecture = today + datetime.timedelta(days=-weekday+2)
        return self.prev_lecture


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME458_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME458_' + date_pat


class tuesday_thursday_course(course):
    def next_lecture_date(self, date=None, force_next=False):
        today = get_valid_date(date=date, force_next=force_next)
        #lectures are on weekdays 1 and 3 (Tuesday and Thursday)
        weekday = today.weekday()
        if weekday in [1,3]:
            self.next_lecture = today
        elif weekday in [0,2]:
            self.next_lecture = today + datetime.timedelta(days=1)
        else:
            self.next_lecture = find_next_day(today, \
                                              des_day=1)#find next Monday
        return self.next_lecture


    def previous_lecture_date(self, date=None, force_next=False):
        today = get_valid_date(date=date, force_next=force_next)
        #lectures are on weekdays 1 and 3 (Tuesday and Thursday)
        weekday = today.weekday()
        ## if weekday == 6:#Sunday --> prev. Thurs..
        ##     self.prev_lecture = today + datetime.timedelta(days=-3)
        if weekday in [0,1]:#Monday or Tuesday --> prev. Thurs.
            delta = -4 - weekday
        elif weekday in [2,3]:#Wed. or Thurs. --> Tues.
            delta = 1 - weekday
        elif weekday in [4,5,6]:#backup to Thurs.
            delta = 3 - weekday
        self.prev_lecture = today + datetime.timedelta(days=delta)
        return self.prev_lecture


class thursday_only_course(course):
    def next_lecture_date(self, date=None, force_next=False):
        today = get_valid_date(date=date, force_next=force_next)
        #lectures are on weekdays 1 and 3 (Tuesday and Thursday)
        weekday = today.weekday()
        if weekday == 3:
            self.next_lecture = today
        elif weekday in [0,1,2]:
            td = 3-weekday
            self.next_lecture = today + datetime.timedelta(days=td)
        else:
            self.next_lecture = find_next_day(today, \
                                              des_day=3)#find next Thursday
        return self.next_lecture


    def previous_lecture_date(self, date=None, force_next=False):
        today = get_valid_date(date=date, force_next=force_next)
        #lectures are on weekdays 1 and 3 (Tuesday and Thursday)
        weekday = today.weekday()
        ## if weekday == 6:#Sunday --> prev. Thurs..
        ##     self.prev_lecture = today + datetime.timedelta(days=-3)
        if weekday in [0,1,2]:#Monday or Tuesday --> prev. Thurs.
            delta = -3 - weekday
        elif weekday == 3:#Wed. or Thurs. --> Tues.
            delta = -7
        elif weekday in [4,5,6]:#backup to Thurs.
            delta = 3 - weekday
        self.prev_lecture = today + datetime.timedelta(days=delta)
        return self.prev_lecture


class course_482(tuesday_thursday_course):
    ## def run(self, date=None, build_previous=False):
    ##     course.run(self, date=date, build_previous=build_previous)

    def __init__(self, path=None, forward=True):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/482/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        tuesday_thursday_course.__init__(self, path)
        self.forward = forward
        self.course_num = '482'


    ## def next_lecture_date(self, date=None):
    ##     today = get_valid_date(date=date, force_next=force_next)
    ##     #482 lectures are on weekdays 1 and 3 (Tuesday and Thursday)
    ##     weekday = today.weekday()
    ##     if weekday in [1,3]:#Tuesday or Thursday
    ##         self.next_lecture = today
    ##     elif weekday in [0,2]:#Monday or Wednesday
    ##         self.next_lecture = today + datetime.timedelta(days=1)
    ##     else:
    ##         self.next_lecture = find_next_day(today, \
    ##                                           des_day=1)#find next
    ##                                                     #Tuesday
    ##     return self.next_lecture


    ## def previous_lecture_date(self, date=None, force_next=False):
    ##     today = get_valid_date(date=date, force_next=force_next)
    ##     #482 lectures are on weekdays 1 and 3 (Tuesday and Thursday)
    ##     weekday = today.weekday()
    ##     if weekday == 6:#Sunday --> prev. Thur.
    ##         self.prev_lecture = today + datetime.timedelta(days=-3)
    ##     elif weekday == [0,1]:#Monday or Tues. --> prev. Thur.
    ##         delta = -4 - weekday
    ##         self.prev_lecture = today + datetime.timedelta(days=delta)
    ##     elif weekday in [2,3]:#backup to Tues.
    ##         self.prev_lecture = today + datetime.timedelta(days=(-weekday+1))
    ##     elif weekday == [4,5]:#backup to Thurs.
    ##         self.prev_lecture = today + datetime.timedelta(days=(-weekday+3))
    ##     return self.prev_lecture

    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME482_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME482_' + date_pat


class course_IE_106(tuesday_thursday_course):
    ## def run(self, date=None, build_previous=False):
    ##     course.run(self, date=date, build_previous=build_previous)

    def __init__(self, path=None, forward=False):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/IE_106/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        tuesday_thursday_course.__init__(self, path)
        self.forward = forward
        self.course_num = '106'


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'IE106_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'IE106_' + date_pat
    

class course_492(course_458):#tuesday_thursday_course):
    def __init__(self, path=None, forward=False):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/mobile_robotics/' + \
                   today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        tuesday_thursday_course.__init__(self, path)
        self.course_num = '492'
        self.forward = forward

    ## def next_lecture_date(self, date=None):
    ##     today = get_valid_date(date=date, force_next=force_next)
    ##     #482 lectures are on weekdays 1 and 3 (Tuesday and Thursday)
    ##     weekday = today.weekday()
    ##     if weekday == 2:#Wednesday
    ##         self.next_lecture = today
    ##     elif weekday == 0:#Monday or Wednesday
    ##         self.next_lecture = today + datetime.timedelta(days=2)
    ##     elif weekday == 1:#Monday or Wednesday
    ##         self.next_lecture = today + datetime.timedelta(days=1)
    ##     else:
    ##         self.next_lecture = find_next_day(today, \
    ##                                           des_day=2)#find next
    ##                                                     #Wednesday
    ##     return self.next_lecture


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME492_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME492_' + date_pat



class nonlinear_controls(tuesday_thursday_course):
    def __init__(self, path=None, forward=True):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/nonlinear_controls/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        tuesday_thursday_course.__init__(self, path)
        self.course_num = '592'
        self.forward = forward


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME592_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME592_' + date_pat


#class course_484(course_458):#<-- I am using 458 as a base class for MW classes
class course_484(tuesday_thursday_course):
    def __init__(self, path=None, forward=False):
        if path is None:
            #today = datetime.date.today()
            today = get_valid_date()
            path = '~/siue/classes/484/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        tuesday_thursday_course.__init__(self, path)
        self.course_num = '484'
        self.forward = forward


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME484_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME484_' + date_pat


class course_592(thursday_only_course):
    def __init__(self, path=None, forward=False):
        if path is None:
            #today = datetime.date.today()
            today = get_valid_date()
            path = '~/siue/classes/592/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        thursday_only_course.__init__(self, path)
        self.course_num = '592'
        self.forward = forward


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME592_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME592_' + date_pat


class course_450_tr(tuesday_thursday_course):
    """450 offered on Tuesdays and Thursdays"""
    def __init__(self, path=None, forward=True):
        if path is None:
            today = datetime.date.today()
            #path = '~/siue/classes/450/' + today.strftime('%Y')#4 digit year
            path = '~/siue/classes/Fall_2015/450_Fall_2015'
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        tuesday_thursday_course.__init__(self, path)
        self.forward = forward
        self.course_num = '450'


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME450_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME450_' + date_pat


    
class course_450_mwf(course_458):
    """This is a MWF class."""
    def __init__(self, path=None, forward=False):
        if path is None:
            #today = datetime.date.today()
            today = get_valid_date()
            path = '~/siue/classes/450/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        course_458.__init__(self, path)
        self.course_num = '450'
        self.forward = forward


    def next_lecture_date(self, date=None, force_next=False):
        today = get_valid_date(date=date, force_next=force_next)

        #458 lectures are on weekdays 0 and 2 and 4 (Monday, Wednesday, and Friday)
        weekday = today.weekday()

        if weekday in [0,2,4]:
            self.next_lecture = today
        elif weekday in [1,3]:
            self.next_lecture = today + datetime.timedelta(days=1)
        else:
            self.next_lecture = find_next_day(today, \
                                              des_day=0)#find next Monday
        return self.next_lecture


    def previous_lecture_date(self, date=None, force_next=False):
        today = get_valid_date(date=date, force_next=force_next)
        #458 lectures are on weekdays 0 and 2 (Monday and Wednesday)
        weekday = today.weekday()
        if weekday in [5,6]:#Saturday or Sunday --> prev. Wed.
            self.prev_lecture = today + datetime.timedelta(days=-weekday+4)
        elif weekday == 0:#Monday --> prev. Fri.
            self.prev_lecture = today + datetime.timedelta(days=-3)
        elif weekday in [1,2]:#backup to Mon.
            self.prev_lecture = today + datetime.timedelta(days=-weekday)
        elif weekday in [3,4]:#backup to Wed.
            self.prev_lecture = today + datetime.timedelta(days=-weekday+2)
        return self.prev_lecture


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME450_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME450_' + date_pat


class course_452(tuesday_thursday_course):
    def __init__(self, path=None, forward=True):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/452/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        tuesday_thursday_course.__init__(self, path)
        self.course_num = '452'
        self.forward = forward


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME452_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME452_' + date_pat


#class course_454(tuesday_thursday_course):
class course_454(course_458):
    def __init__(self, path=None, forward=True):
        if path is None:
            today = datetime.date.today()
            path = '~/siue/classes/454/' + today.strftime('%Y')#4 digit year
            path += '/lectures/'
        #self.path = rwkos.FindFullPath(path)
        #tuesday_thursday_course.__init__(self, path)
        course_458.__init__(self, path)
        self.course_num = '454'
        self.forward = forward


    def build_pat(self):
        date_pat = self.next_lecture.strftime('%m_%d_%y')
        self.pat = 'ME454_' + date_pat + '_%0.4i.xcf'
        self.search_pat = 'ME454_' + date_pat
