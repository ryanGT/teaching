"""I am writing some utilities to work with the processing of class
lists and transcripts from Brad Noble's perl code.

Don't forget to use the -a option when generating the classlist:

classlist.sh -a IME 106 FR3 201415 > sec_FR3_classlist.txt
"""

import txt_mixin, csv_to_latex, rwkos
import os, re, glob
import numpy
from numpy import array, arange

from bs4 import BeautifulSoup

from IPython.core.debugger import Pdb

mod_debug = 1#debug print statements for the module

import copy

banner_id_pat = re.compile('(800[0-9]+)')


def semester_str_to_pretty_str(semester_in):
    """Convert strings like '201435' to something pretty and easy to
    read like Fall_2014."""
    year_str = semester_in[0:4]
    sem_key = semester_in[-2:]
    sem_dict = {'15':'Spring', \
                '25':'Summer', \
                '35':'Fall'}
    pretty_str = '%s_%s' % (sem_dict[sem_key], year_str)
    return pretty_str

    
def parse_one_name(string_in):
    last, rest = string_in.split(',',1)
    last = last.strip()
    rest = rest.strip()
    if rest.find(' ') > -1:
        first, rest2 = rest.split(' ',1)
        first = first.strip()
    else:
        first = rest
    return last, first

email_pat = re.compile('<(.*)>')

def parse_one_email_string(string_in):
    q = email_pat.search(string_in)
    return q.group(1)



class classlist_puller(object):
    """Class to support pulling a classlist using Brad Noble's perl
    script.  semester needs to be one of '15' (spring), '25' (summer),
    or '35' (fall).  I am trying to make this function also accept
    'spring', 'summer', or 'fall'.  Ultimately, we need a string like
    this one:

    cmd = 'classlist.sh -a ME 482 001 201415 > ' + pathout
    """
    def __init__(self, course_num, section, year, semester, \
                 folder='', subject='ME'):
        
        if type(semester) == int:
            semester = '%i' % semester
        elif semester not in ['15','25','35']:
            key = semester[0:3].lower()
            sem_dict = {'spr':15,'sum':25,'fal':'35'}
            semester = sem_dict[key]

        year = str(year)

        if type(course_num) == int:
            course_num = '%0.3i' % course_num
        else:
            course_num = str(course_num)

        if type(section) == int:
            section = '%0.3i' % section

        self.course_num = course_num
        self.section = section
        self.year = year
        self.semester = semester
        self.folder = folder
        self.subject = subject
        

    def build_filename(self):
        fn = '%s%s_%s_%s%s_classlist.txt' % (self.subject, \
                                             self.course_num, \
                                             self.section, \
                                             self.year, \
                                             self.semester)
        self.filename = fn
        self.pathout  = os.path.join(self.folder, self.filename)
        return self.pathout
    

    def _build_cmd(self):
        cmd = 'classlist.sh -a %s %s %s %s%s > %s' % (self.subject, \
                                                      self.course_num, \
                                                      self.section, \
                                                      self.year, \
                                                      self.semester, \
                                                      self.pathout)
        self.cmd = cmd
        return self.cmd


    def pull(self):
        self._build_cmd()
        os.system(self.cmd)


    def exists(self):
        if not hasattr(self, 'pathout'):
            self.build_filename()
        return os.path.exists(self.pathout)


class name_replacer(object):
    """Class to replace first names in a class list with a preferred
    alternate name.  I am going to require that the last name and
    given first name both match before a replacment is done so that I
    don't require everyone named Smith to change their first name."""
    def __init__(self, arrayin):
        """arrayin must have 3 columns: last name, given first name,
        preferred name"""
        nr, nc = arrayin.shape
        assert nc == 3, "arrayin for name_replacer class must have 3 colums"
        self.array = arrayin
        self.lastnames = arrayin[:,0].tolist()
        self.given_firsts = arrayin[:,1].tolist()
        self.alt_firsts = arrayin[:,2].tolist()


    def search_one_name(self, lastname, firstname):
        if lastname in self.lastnames:
            ind = self.lastnames.index(lastname)
            fn_check = self.given_firsts[ind]
            if fn_check == firstname:
                #we have a match
                return self.alt_firsts[ind]
            
        
    
class classlist_parser(txt_mixin.txt_file_with_list):
    def get_row(self, index):
        """output a clean row list that contains
        [lastname, firstname, studentid, grade]"""
        attrs = ['lastnames','firstnames','studentid','grade']
        rowout = []

        for attr in attrs:
            vector = getattr(self, attr)
            val = vector[index]
            rowout.append(val)

        return rowout
    

    def get_data_from_list_of_rows(self, index_list):
        listout = []

        for index in index_list:
            row = self.get_row(index)
            listout.append(row)

        return listout
    
        
    def filter_by_grades(self, good_grades=['A','B','C']):
        """Search through the Grades column and find all grades not in
        A-C."""
        keep_inds = []

        grades_col = self.col_labels.index('Grade')

        for i, row in enumerate(self.array):
            grade = row[grades_col]
            if grade not in good_grades:
                keep_inds.append(i)

        #self.grades = self.get_col(grades_col)
        listout = self.get_data_from_list_of_rows(keep_inds)
        return listout


    def find_inds(self):
        """Find the indices for the start of each column after the
        first one."""
        labels = self.col_labels[1:]
        inds = []
        label_row = self.list[0]
        for item in labels:
            ind = label_row.find(item)
            inds.append(ind)

        self.col_inds = inds
        

    def break_rows(self):
        """Break each row string into columns based on the column
        widths/inds found using self.find_inds"""
        listout = []

        for row in self.list[1:]:
            prev_ind = 0
            row_list = []
            for ind in self.col_inds:
                chunk = row[prev_ind:ind]
                row_list.append(chunk)
                prev_ind = ind

            last_chunk = row[prev_ind:]
            row_list.append(last_chunk)
            
            listout.append(row_list)

        self.raw_nested_list = listout


    def strip_items(self):
        listout = []

        for row in self.raw_nested_list:
            row_list = []
            for item in row:
                item2 = item.strip()
                row_list.append(item2)
            listout.append(row_list)

        self.nested_list = listout


    def get_col(self, ind):
        col = self.array[:,ind]
        return col
    

    def get_banner_ids(self):
        self.banner_ids = self.get_col(2)
        return self.banner_ids


    def get_levels(self):
        self.levels = self.get_col(4)
        return self.levels


    def get_email_strings(self):
        return self.get_col(-1)


    def parse_emails(self):
        email_strings = self.get_email_strings()
        test_email = email_strings[0]
        assert test_email.find('@siue.edu') > -1, "problem with email string check : %s" % test_email
        clean_emails = [parse_one_email_string(item) for item in email_strings]
        self.emails = clean_emails
    
        
    def parse(self):
        """Assuming self.list already exists, determine the width of
        the fixed with columns and break each line into columns.

        This will be hard coded a bit to the known format of the fixed
        width files Brad's code generates.  The first row contains the
        labels.  The first label is not needed."""
        self.find_inds()
        self.break_rows()
        self.strip_items()
        self.array = array(self.nested_list)



    
    def assign_cols_to_attrs(self):
        from txt_database import label_to_attr_name

        for i, label in enumerate(self.col_labels):
            if label == '#':
                attr = 'num'
            else:
                attr = label_to_attr_name(label)
            attr = attr.lower()
            col = self.get_col(i)
            setattr(self, attr, col)
        
        
    def __init__(self, *args, **kwargs):
        txt_mixin.txt_file_with_list.__init__(self, *args, **kwargs)
        self.col_labels = ['#','Name','StudentID','Stat','Lvl','Grade','e-Mail Address']
        self.parse()
        self.assign_cols_to_attrs()
        self.parse_names()
        self.parse_emails()


    def replace_names(self, replacer):
        """Replace first names if students strongly prefer to be
        called something else and make this known before class starts."""
        N = len(self.name_strs)
        n_list = arange(N)
        
        for i, last, first in zip(n_list, self.lastnames, self.firstnames):
            alt_name = replacer.search_one_name(last, first)
            if alt_name:
                self.firstnames[i] = alt_name
            

    def parse_names(self, force=False):
        if hasattr(self,'lastnames') and not force:
            #do nothing
            return
        self.name_strs = self.get_col(1)
        lastnames = []
        firstnames = []

        for item in self.name_strs:
            last, first = parse_one_name(item)
            lastnames.append(last)
            firstnames.append(first)

        self.lastnames = lastnames
        self.firstnames = firstnames


    def append_file(self, filename):
        """Append a second classlist.  This would be used for example
        with robotics where there are two classlists (ME 454 and ECE
        467) that need to be combined into one effective classlist."""
        newlist = classlist_parser(filename)
        new_array = numpy.row_stack([self.array, newlist.array])
        big_list = new_array.tolist()
        name_col = self.col_labels.index('Name')
        #sort by Name
        big_list.sort(key=lambda item: item[name_col])
        self.array = array(big_list)
        self.assign_cols_to_attrs()
        self.parse_names()
        self.parse_emails()
        
        
        
    def build_csv_classlist(self):
        #Last Name,First Name,ID,Please Call Me,Email Address
        #Bailey,Adam,800512776,,
        #Burley,Keith,800486675,,
        #Dickinson,Alexander,800508999,,
        self.parse_names()
        self.banner_ids = self.get_banner_ids()

        nested_out = []
        
        for last, first, banner_id in zip(self.lastnames, self.firstnames, self.banner_ids):
            rowout = [last, first, banner_id, '', '']
            nested_out.append(rowout)

        return nested_out


    def build_data(self, attrlist):
        """Return an array whose columns are the items in attrlist"""
        data = []

        for attr in attrlist:
            vect = getattr(self, attr)
            data.append(vect)

        array_out = numpy.column_stack(data)
        return array_out

        
    def make_latex_list(self, pathout, extra_col_labels=None, **kwargs):
        """Create a classlist that is ready for pdflatex for use on
        the first day of class for getting preferred emails or nicknames."""
        names_array = self.build_data(['lastnames','firstnames'])
        names_list = names_array.tolist()
        hrule = None
        if extra_col_labels is not None:
            hrule='\\rule{2.0in}{0pt}'
        latex_out = csv_to_latex.csv_to_latex_table(names_list, labels=['Lastname','Firstname'], \
                                                    extra_col_labels=extra_col_labels, \
                                                    hrule=hrule, **kwargs)
        txt_mixin.dump(pathout, latex_out)


    def build_email_csv_list_for_import(self):
        if not hasattr(self, 'lastnames'):
            self.parse_names()
        self.parse_emails()

        nested_out = []

        for last, first, email in zip(self.lastnames, self.firstnames, self.emails):
            rowout = [last, first, email]
            nested_out.append(rowout)

        return nested_out


    def save_email_csv_classlist(self, pathout=None):
        if pathout is None:
            fno, ext = os.path.splitext(self.pathin)
            pathout = fno + '_email_list.csv'

        mylist = self.build_email_csv_list_for_import()
        labels = ['Last Name','First Name', 'Email']

        txt_mixin.dump_delimited(pathout, mylist, delim=',', labels=labels)


    def save_csv_classlist(self, pathout=None):
        if pathout is None:
            fno, ext = os.path.splitext(self.pathin)
            pathout = fno + '_out.csv'

        mylist = self.build_csv_classlist()
        labels = ['Last Name','First Name', 'ID', 'Please Call Me','Email Address']

        txt_mixin.dump_delimited(pathout, mylist, delim=',', labels=labels)
        
            
        



def process_one_table_row(row_list, delim='|'):
    rowstr = ''
    for td in row_list:
        text = None
        if td.find(text=True):
            text = ''.join(td.find(text=True))
            text = text.replace('&nbsp',' ')
            text = text.replace(u'\xa0', u' ')
            text = text.strip()
            rowstr += text + delim

    return rowstr


def transcript_html_to_txt_list(filename, delim='|'):
    soup = BeautifulSoup(open(filename))

    body = soup.body
    rows = body.findAll('tr')

    listout = []

    for tr in rows:
        headers = tr.findAll('th')
        header_str = ''
        if headers:
            header_str = process_one_table_row(headers, delim=delim)

        cols = tr.findAll('td')
        cols_str = ''
        if cols:
            cols_str = process_one_table_row(cols, delim=delim)

        rowstr = header_str + cols_str

        if rowstr and rowstr[-1] == delim:
            rowstr = rowstr[0:-1]

        listout.append(rowstr.encode())

    return listout



class transcript_html_parser(object):
    def save(self, txt_path=None, folder=''):
        if txt_path is None:
            txt_path = os.path.join(folder, self.txt_filename)

        txt_mixin.dump(txt_path, self.txt_list)
        
        
    def __init__(self, filename):
        self.html_path = filename
        self.folder, self.html_filename = os.path.split(self.html_path)
        fno, ext = os.path.splitext(self.html_filename)
        self.txt_filename = fno + '.txt'

        self.txt_list = transcript_html_to_txt_list(self.html_path)



class class_schedule_parser(txt_mixin.txt_file_with_list):
    """The first step in my undergraduate committee work of finding
    out who should be on probation is generating a list of all ME
    courses taught in a given semester.  This was done manually in the
    past.  In Dec. 2014 I am deciding to manually do a search for ME
    courses and save the results to an html file.  I will then use
    this class to extract all course names, CRNs, and sections from
    that html file."""
    def __init__(self, pathin, **kwargs):
        txt_mixin.txt_file_with_list.__init__(self, pathin, **kwargs)
        self.title_line_pat = re.compile('(<TH.*?>)<A (.*?)>(.*)</A></TH>')
        self.build_pathout()
        

    def build_pathout(self):
        pne, ext = os.path.splitext(self.pathin)
        pathout = pne + '_parsed.csv'
        self.pathout = pathout
        return self.pathout
    

    def find_title_inds(self):
        title_inds = self.list.findall('<TH CLASS="ddtitle"', forcestart=1)
        self.title_inds = title_inds


    def get_raw_title_lines(self):
        raw_title_lines = []

        for ind in self.title_inds:
            raw_title_lines.append(self.list[ind])

        self.raw_title_lines = raw_title_lines


    def parse_one_title_line(self, linein):
        q = self.title_line_pat.search(linein)
        assert q, "problem with regexp match for line: %s" % linein
        return q.group(3)


    def extract_titles_from_raw_lines(self):
        self.course_titles = []

        for line in self.raw_title_lines:
            title = self.parse_one_title_line(line)
            self.course_titles.append(title)
            

    def break_one_title(self, title_in):
        """The course titles appear to be hyphen delimited with spaces
        around the hyphens.  There also appears to be four elements to
        the title, the course name, the CRN, the course number, and
        the section number."""
        row_list = title_in.split('-')
        assert len(row_list) == 4, "problem with number of items in hyphen delimited row: %s" % title_in
        clean_row = [item.strip() for item in row_list]
        return clean_row


    def break_titles(self):
        data = []

        for title in self.course_titles:
            cur_row = self.break_one_title(title)
            data.append(cur_row)

        self.data = data
        
        
        
    def parse(self):
        self.find_title_inds()
        self.get_raw_title_lines()
        self.extract_titles_from_raw_lines()
        self.break_titles()


    def save(self):
        mylabels = ['course name','CRN','course number','section']
        txt_mixin.dump_delimited(self.pathout, self.data, \
                                 delim=',', labels=mylabels)
        
    
def append_delim_to_pat(pat_in, delim):
    """the pipe delim that I like right now needs to be escaped in
    regexp patterns."""
    pat = pat_in
    
    if delim == '|':
        pat += '\\' + delim
    else:
        pat += delim

    return pat


def pop_empty_from_end(listin):
    while not listin[-1]:
        listin.pop(-1)
    return listin


name_pat = re.compile('^([A-z]+) ([A-Z])\. ([A-z ]+)$')
name_pat_no_mi = re.compile('^([A-z]+) ([A-z ]+)$')


other_subjects = ['AD','POLS','ENG','PHIL','SOC','THEA', \
                  'PSYC','ECON','SPC',]

class transcript_txt_parser(txt_mixin.txt_file_with_list):
    def break_name(self):
        name = self.get_name()
        q = name_pat.match(name)
        if q:
            self.first_name = q.group(1)
            self.mi = q.group(2)
            self.last_name = q.group(3)
        else:
            q = name_pat_no_mi.match(name)
            self.first_name = q.group(1)
            self.mi = ''
            self.last_name = q.group(2)
            
        
    def _get_one_line(self, pat, match=False):
        inds = self.list.findallre(pat, match=match)
        assert len(inds) == 1, "did not find exactly one match for " + pat
        return self.list[inds[0]]


    def _get_first_line(self, pat, match=False):
        """College:delim may match many times; I just want the first
        one, which should be the current one."""
        inds = self.list.findallre(pat, match=match)
        return self.list[inds[0]]

    
    def get_regexp_matches(self, pat, match=False):
        listout = []
        inds = self.list.findallre(pat, match=match)
        for ind in inds:
            line = self.list[ind]
            listout.append(line)

        return listout


    def get_major_and_dept(self):
        pat = append_delim_to_pat('^Major and Department:', self.delim)
        line = self._get_one_line(pat)
        junk, m_and_d_str = line.split(self.delim, 1)
        major, dept = m_and_d_str.split(',',1)
        self.major = major.strip()
        self.dept = dept.strip()
        return self.major, self.dept


    def get_college(self):
        pat = append_delim_to_pat('^College:', self.delim)
        line = self._get_first_line(pat)
        junk, college = line.split(self.delim, 1)
        self.college = college.strip()
        return self.college


    def get_and_print_regexp(self, pat, **kwargs):
        listout = self.get_regexp_matches(pat, **kwargs)
        for line in listout:
            print(line)
            

    def get_name(self):
        pat = append_delim_to_pat('^Name *:', self.delim)
        inds = self.list.findallre(pat)
        assert len(inds) == 1, "did not find exactly one match for " + pat
        ind = inds[0]
        name_row = self.list[ind]
        junk, name = name_row.split(self.delim, 1)
        return name


    def get_subject_lines(self, subject):
        pat = '^' + subject
        pat = append_delim_to_pat(pat, self.delim)
        linesout = self.get_regexp_matches(pat)
        return linesout


    def split_row_to_list(self, rowstr):
        """split row using self.delim and pop empty elements from the
        end"""
        course_list = rowstr.split(self.delim)
        while not course_list[-1]:
            course_list.pop(-1)
        return course_list


    def get_grade_form_line(self, line):
        """split a line into a list and grab the -3 element"""
        line_list = self.split_row_to_list(line)
        grade = line_list[-3]
        all_grades = ['A','B','C','D','F','S','NS','W','WP','WF','UW','WR','I']
        assert grade in all_grades, "Invalid grade: %s" % grade
        return grade
        

    def gpa_from_list_of_lines(self, lines):
        credit_hours = []
        quality_points = []

        valid_grades = ['A','B','C','D','F']#not sure what to do with
                                            #W right now
        

        for course_row in lines:
            course_list = self.split_row_to_list(course_row)
            skip = False
                
            if not skip:
                assert len(course_list) == 8, "bad grade row: " + course_row
                qp = float(course_list[-1])
                ch = float(course_list[-2])
                letter_grade = course_list[-3]
                if letter_grade in valid_grades:
                    credit_hours.append(ch)
                    quality_points.append(qp)
                else:
                    error_str = self.delim.join(course_list[0:2] + \
                                                course_list[-3:]) 
                    print('skipping: ' + error_str)

        num = numpy.sum(quality_points)
        den = numpy.sum(credit_hours)
        if den == 0.0:
            gpa = None
        else:
            gpa = float(num)/float(den)

        return gpa


    def modify_lines_ending_in_E_and_I(self, lines):
        """Lines ending in E or I are tricky and may not affect term
        GPA, but I am pretty sure they still count for how many times
        a course has been dropped.  So, this method will be used with
        find_repeated_failures_and_withdraws to make the lines ending
        in E and I look like regular lines (by dropping the last two
        elements in the in)."""

        # - find lines with 10 elements where the last element is E or I
        # - keep only elements [0:8]
        # - rebuild the list into a string
        # - return the newlist with regular lines unmodified

        listout = []

        for line in lines:
            cur_list = self.split_row_to_list(line)
            if len(cur_list) == 8:
                #do nothing, pass it through
                listout.append(line)
            elif len(cur_list) == 10:
                last_item = cur_list.pop(-1)
                assert last_item in ['E','I'], "Invalid last item in row of length 10: %s" % last_item
                empty_item = cur_list.pop(-1).strip()
                assert empty_item == '', "This item should have been empty in row of length 10: %s" % empty_item
                new_line = self.delim.join(cur_list)
                listout.append(new_line)

        return listout


    def handle_lines_ending_in_E_and_I(self, lines):
        """If a grade row ends in E, it seems not to count in the term
        GPA, so I am assuming it is a special case and I am dropping
        those rows.  A row ending in I appears to be an incomplete
        that is latter filled in."""
        lineouts = []

        for course_row in lines:
            course_list = self.split_row_to_list(course_row)
            skip = False
            if course_list[-1] == 'E':
                #I guess these are skipped
                skip = True
            elif course_list[-1] == 'I':
                #I don't think these are skipped
                course_list.pop(-1)
                course_list = pop_empty_from_end(course_list)
                course_row = self.delim.join(course_list)
            if not skip:
                lineouts.append(course_row)

        return lineouts


    def filter_passing_grades(self, lines):
        """Given a list of transcript lines, filter out the ones with
        passing grades.  This is done to try to find instances where a
        student has failed or withdrawn from a course more than twice."""
        linesout = []

        passing_grades = ['A','B','C','D','S']

        for line in lines:
            cur_grade = self.get_grade_form_line(line)
            if cur_grade not in passing_grades:
                linesout.append(line)

        return linesout
        

    def filter_inprogress_courses(self, lines):
        """After scrubbing off empty elements from the end of the
        list, completed courses should have 8 elements per row, while
        inprogress coures have 6."""
        linesout = []

        for course_row in lines:
            course_list = self.split_row_to_list(course_row)
            if len(course_list) == 8:
                linesout.append(course_row)
            elif len(course_list) != 6:
                raise ValueError, "problem with this course_list: " + \
                      str(course_list)

        return linesout



    def get_filtered_non_passing_lines(self, subject):
        """Get the lines for ^subject that were not passed, filtering
        out inprogress courses."""
        subject_lines = self.get_subject_lines(subject)
        subject_lines_modified = self.modify_lines_ending_in_E_and_I(subject_lines)
        subject_lines_filt = self.filter_inprogress_courses(subject_lines_modified)
        non_passing_subject_lines = self.filter_passing_grades(subject_lines_filt)
        return non_passing_subject_lines



    def key_from_line(self, line):
        """Make a dictionary key from a transcript line.  This will be
        used in a dictionary to count withdraws and failures"""
        line_list = self.split_row_to_list(line)
        subject = line_list[0]
        course = line_list[1]
        key = subject+course
        return key


    def nonpassing_lines_to_dict(self, lines):
        """take a list of lines composed of nonpassing courses and
        convert them to a dictionary so that we can count how many
        times each course has been dropped or failed."""
        mydict = {}

        for line in lines:
            key = self.key_from_line(line)
            cur_grade = self.get_grade_form_line(line)
            if mydict.has_key(key):
                mydict[key].append(cur_grade)
            else:
                mydict[key] = [cur_grade]

        return mydict


    def check_dict_for_too_many_non_passing_grades(self, mydict):
        bad_dict = {}

        for key, value in mydict.iteritems():
            if len(value) > 2:
                bad_dict[key] = value

        return bad_dict
    
        
    def find_repeated_failures_and_withdraws(self):
        """Find all courses with repeated failures or withdraws
        following these steps:

         - find all ME courses
         - find all grades that are not A-D
         - count the number of instances of each course
         - verify that any course failed or withdrawn from multiple times is not an elective
        """
        subject_list = ['ME']#the UG catalog says required courses in
                             #the major, I don't know if that just
                             #means ME or all courses required for the degree,
                             #assuming just ME for now

        non_passing_lines = []

        for subject in subject_list:
            cur_lines = self.get_filtered_non_passing_lines(subject)
            non_passing_lines.extend(cur_lines)


        mydict = self.nonpassing_lines_to_dict(non_passing_lines)
        bad_dict = self.check_dict_for_too_many_non_passing_grades(mydict)
        self.non_passing_dict = mydict
        self.too_many_dict = bad_dict
        return mydict, bad_dict

            

    def filt_subject_lines_below_300(self, lines):
        linesout = []

        for course_row in lines:
            keep = False
            course_list = course_row.split(self.delim)
            num_str = course_list[1].strip()
            try:
                course_num = int(num_str)
                if course_num > 299:
                    keep = True
            except ValueError:
                if num_str[-1] == 'L':
                    course_num = int(num_str[0:-1])#drop the L
                    if course_list > 299:
                        keep = True
            if keep:
                linesout.append(course_row)

        return linesout


    def probation_check(self, term, year, term_gpa=1.0):
        """Check to see if the student should be placed on academic
        probation or suspension. term (Spring or Fall) and year are
        used to find the GPA for the current term.  The UG catalog
        lists 6 criteria:

          - Maintain a cumulative grade point average of 2.0. 
         
          - Maintain a term grade point average above 1.0 in any term. 
         
          - Maintain a cumulative grade point average of at least 2.0
            in all mathematics and science courses. 
         
          - Maintain cumulative grade point average of at least a 2.0
            in courses taught in the School of Engineering. 
         
          - Maintain a cumulative grade point average of at least 2.0
            in major courses numbered above 299. 
         
          - Receive no more than two failure grades, incomplete, and/or
            withdrawals in any combination for a single course required
            in the major.

        I am allowing term_gpa to be a variable so that I can set it
        to 2.0 when checking if a student should be restored to good
        standing (a student who was already on probation).  I don't
        think you can get the rest of the requirements back above 2.0
        and have a term GPA below 2.0, but I want to have this as a
        personal extra check.  If everything else passes, but your
        term GPA is still below 2.0, I don't think you should be
        restored to good standing.
        """
        
        cum_gpa = self.find_overall_gpa()
        cur_term_gpa = self.find_term_GPA(term, year)
        math_science_gpa = self.find_math_and_science_GPA()
        SOE_gpa = self.find_SOE_gpa()
        me_299_gpa_mod = self.find_ME_299_plus_gpa()
        mydict, bad_dict = self.find_repeated_failures_and_withdraws()#sets self.too_many_dict = bad_dict

        probation = False

        gpa_list_2_0 = [cum_gpa, math_science_gpa, SOE_gpa, me_299_gpa_mod]

        def test_gpa(gpain, cutoff=2.0):
            """Allow GPAs of None to not trigger probation.  A bad GPA
            is a probation trigger."""
            bad = False
            if gpain is not None:
                if gpain < cutoff:
                    bad = True
            return bad

        for gpa in gpa_list_2_0:
            if test_gpa(gpa):
                probation = True
                break

        if not probation:
            #only keep checking if we haven't already triggered probation
            if test_gpa(cur_term_gpa, term_gpa) or (len(self.too_many_dict) > 0):
                probation = True
            
            
        ## if (cum_gpa < 2.0) or (cur_term_gpa < 1.0) or (math_science_gpa < 2.0) or \
        ##    (SOE_gpa < 2.0) or (me_299_gpa_mod < 2.0):
        ##     probation = True
        ## elif len(self.too_many_dict) > 0:
        ##     probation = True

        return probation


    def probation_spreadsheet_rowlist(self, fmt='%0.4g', restore=False):
        """Convert the 6 criteria in probation_check into a
        spreadsheet row for the student to be used in discussion with
        the UG committee and the chair."""

        my_float_list = [self.cum_gpa, self.cur_term_gpa, self.ms_gpa, \
                         self.SOE_gpa, self.ME_299_plus_gpa]

        def gpa_to_str(gpa):
            if gpa is None:
                return 'NA'
            else:
                return fmt % gpa

        str_list = [gpa_to_str(item) for item in my_float_list]

        #too many failures or withdraws
        if len(self.too_many_dict) > 0:
            too_many_str = str(self.too_many_dict)
            too_many_str = too_many_str.replace(',',';')
        else:
            too_many_str = ''

        str_list.append(too_many_str)

        if restore:
            restore_bool = self.restore_check()
            if restore_bool:
                str_list.append('Y')
            else:
                str_list.append('N')

        self.break_name()
        outlist = [self.last_name, self.first_name] + str_list
        return outlist


    def restore_check(self, term=None, year=None):
        """Check to see if a student who was previously on probation
        should be restored to good standing.  All GPAs including the
        current term GPA should be above 2.0."""
        if term is None:
            term = self.term
        if year is None:
            year = self.year
        restore = not (self.probation_check(term, year, term_gpa=2.0))
        return restore

        
    def probation_spreadsheet_labels(self, restore=False):
        labels = ['Lastname','Firstname','Cum. GPA','Current Term GPA','Math/Science GPA', \
                  'SoE GPA','ME>299 GPA','Too Many Failures or Drops']
        if restore:
            labels.append('Restore to Good Standing')

        return labels
        

    def get_course_nums(self, subject):
        subject_lines = self.get_subject_lines(subject)
        course_nums = []
        for line in subject_lines:
            line_list = line.split(self.delim)
            course_str = line_list[1].strip()
            try:
                cur_num = int(course_str)
                course_nums.append(cur_num)
            except ValueError:
                if course_str[-1] == 'L':
                    course_nums.append(course_str)
                else:
                    print('bad course num: ' + line)

        return course_nums


    def college_check(self):
        self.get_college()
        if self.college != 'School of Engineering':
            return False
        else:
            return True


    def major_check(self):
        self.get_major_and_dept()
        major_check = True
        if self.major.find('Engineering') == -1:
            if self.major != 'Computer Science':
                major_check = False
        return major_check


    def check_for_min_math(self, cutoff=125):
        math_courses = self.get_course_nums('MATH')
        if len(math_courses) == 0:
            return False
        elif numpy.max(math_courses) < cutoff:
            return False
        else:
            return True


    def math_check_IME_106(self):
        return self.check_for_min_math(cutoff=125)

    
    def math_120_check(self):
        return self.check_for_min_math(cutoff=120)


    def IME_check(self):
        """This is an automated to check to see if self.college ==
        School of Engineering and major contains Engineering and
        max(math course nums) >= 125."""
        college_check = self.college_check()
        major_check = self.major_check()
        math_check = self.math_check_IME_106()

        if college_check and major_check and math_check:
            return True
        else:
            return False

        

    def IME_106_report(self):
        """Generate a report to check if a student is a declared
        engineering major or could be so."""
        name = self.get_name()
        listout = ['']
        listout.append('='*40)
        listout.append(name)
        listout.append('='*40)
        listout.append('')
        college_lines = self.get_regexp_matches('^College *:')
        listout.extend(college_lines)
        major_lines = self.get_regexp_matches('^Major')
        listout.extend(major_lines)
        listout.append('')

        #how do you handle no transfer credit or no siue credit?
        transfer_inds = self.list.findallre('^TRANSFER CREDIT ACCEPTED BY INSTITUTION')
        if len(transfer_inds) == 0:
            transfer_ind = None
        else:
            transfer_ind = transfer_inds[0]
        siue_inds = self.list.findallre('^INSTITUTION CREDIT')
        if len(siue_inds) == 0:
            siue_ind = None
        else:
            siue_ind = siue_inds[0]
        inprogress_ind = self.list.findallre('^COURSES IN PROGRESS')[0]
        math_inds = self.list.findallre('^MATH')
        math_inds.sort()

        if transfer_ind is not None:
            listout.append('TRANSFER Math Course(s):')
            listout.append('='*30)
            listout.append('')

            if siue_ind is None:
                stop_ind = inprogress_ind
            else:
                stop_ind = siue_ind
        
            for ind in math_inds:
                if ind < stop_ind:
                    listout.append(self.list[ind])

        if siue_inds is not None:
            listout.append('')
            listout.append('SIUE Completed Math Course(s):')
            listout.append('='*30)
            listout.append('')

            for ind in math_inds:
                if siue_ind < ind < inprogress_ind:
                    listout.append(self.list[ind])

        listout.append('')
        listout.append('In-Progress Math Course(s):')
        listout.append('='*30)
        listout.append('')
        
        for ind in math_inds:
            if ind > inprogress_ind:
                listout.append(self.list[ind])

        return listout


    def IME_spreadsheet_row(self):
        gpa = self.find_overall_gpa()
        self.break_name()
        self.get_major_and_dept()
        currow = [self.last_name, self.first_name, self.mi, \
                  self.major, gpa]
        return currow


    def get_IME_spreadsheet_labels(self):
        mylabels = ['Last Name','First Name','Middle Initial', \
                    'Major','SIUE GPA']
        return mylabels


    def find_overall_gpa(self):
        """Parse txt to find overall gpa using the following steps:

        - find INSTITUTION CREDIT

          - this is the beginning of the SIUE section

        - find TRANSCRIPT TOTALS * below INSTITUTION CREDIT
        - go down a few lines to find
            Overall:|18.000|18.000|18.000|18.000|33.000|1.833
          - pull the last entry (probably check the length of the list)
          - convert it to float
          
        """

        siue_inds = self.list.findallre('^INSTITUTION CREDIT')
        if len(siue_inds) == 0:
            return None
        siue_ind = siue_inds[0]

        totals_inds = self.list.findallre('^TRANSCRIPT TOTALS')
        if len(totals_inds) == 0:
            return None

        #find the totals_ind that is higher that the siue_ind (start
        #of siue section)
        totals_ind = None

        for ind in totals_inds:
            if ind > siue_ind:
                totals_ind = ind
                break

        if totals_ind is None:
            print('did not find a valid ind for TRANSCRIPT TOTALS')
            print('siue_ind = %i' % siue_ind)
            print('totals_inds = ' + str(totals_inds))
                
        
        ## Unofficial Transcript|Unofficial Transcript
        ## Unofficial Transcript
        ## TRANSCRIPT TOTALS (UNDERGRADUATE)
        ## Attempt Hours|Passed Hours|Earned Hours|GPA Hours|Quality Points|GPA|
        ## Total Institution:|18.000|18.000|18.000|18.000|33.000|1.833
        ## Total Transfer:|0.000|0.000|0.000|0.000|0.000|0.000
        ## Overall:|18.000|18.000|18.000|18.000|33.000|1.833

        pat = append_delim_to_pat('^Overall:', self.delim)
        overall_ind = self.list.findnextre(pat, totals_ind)
        overall_row_str = self.list[overall_ind]
        overall_list = overall_row_str.split(self.delim)
        assert len(overall_list) == 7, "did not seem to get a correct overall list length:\n" + str(overall_list)
        gpa_str = overall_list[-1]
        gpa = float(gpa_str)
        self.cum_gpa = gpa
        return gpa


    def find_term_GPA(self, semester, year):
        """Find the GPA for a specific term (probably normally the
        current term) by searching for
        Term: semester year
        where semester is either Fall, Spring, or Summer and year is 4 digits.

        Then search for the next blank line and verify that the line
        after the blank begins with
        Unofficial Transcript

        Then in that batch of lines for the specified semester find
        a line like this:
        Current Term:|18.000|18.000|18.000|18.000|45.000|2.500
        and grab the last entry and convert it to a float
        """
        ## Example chunk:
        
        ## Unofficial Transcript|Unofficial Transcript
        ## Unofficial Transcript
        ## Term: Spring 2014
        ## College:|School of Engineering
        ## Major:|Industrial Engineering
        ## Student Type:|Continuing
        ## Academic Standing:|Good Standing
        ## Subject|Course|Campus|Level|Title|Grade|Credit Hours|Quality Points|Start and End Dates|R|CEU
        ## CE|242|Edwardsville|UG|Mechanics of Solids|C|3.000|6.000|||
        ## ECE|210|Edwardsville|UG|Circuit Analysis I|B|3.000|9.000|||
        ## ENG|102N|Edwardsville|UG|Eng. Comp: Non-Native Speakers|B|3.000|9.000|||
        ## MATH|305|Edwardsville|UG|Differential Equations I|B|3.000|9.000|||
        ## ME|262|Edwardsville|UG|Dynamics|D|3.000|3.000|||
        ## SPC|103|Edwardsville|UG|Interpersonal Comm Skills|B|3.000|9.000|||
        ## Term Totals (Undergraduate)
        ## Attempt Hours|Passed Hours|Earned Hours|GPA Hours|Quality Points|GPA|
        ## Current Term:|18.000|18.000|18.000|18.000|45.000|2.500
        ## Cumulative:|34.000|34.000|34.000|34.000|80.000|2.353

        ## Unofficial Transcript|Unofficial Transcript
        ## Unofficial Transcript
        ## TRANSCRIPT TOTALS (UNDERGRADUATE)
        ## Attempt Hours|Passed Hours|Earned Hours|GPA Hours|Quality Points|GPA|
        ## Total Institution:|34.000|34.000|34.000|34.000|80.000|2.353
        ## Total Transfer:|42.000|42.000|42.000|0.000|0.000|0.000
        ## Overall:|76.000|76.000|76.000|34.000|80.000|2.353

        self.term = semester
        self.semester = semester
        self.year = year
        
        term_pat = '^Term: %s %s' % (semester, year)
        term_inds = self.list.findallre(term_pat)
        if len(term_inds) == 0:
            self.cur_term_gpa = None
            return None
        assert len(term_inds) == 1, "Did not find exactly one match for a line starting with: %s" % term_pat
        term_ind = term_inds[0]

        #now find next blank line and test that it is followed by "Unofficial Transcript"
        for i in range(100):
            curline = self.list[term_ind + i]
            temp = curline.strip()
            if len(temp) == 0:
                next_line = self.list[term_ind + i + 1]
                search_ind = next_line.find('Unofficial Transcript')
                assert search_ind > -1, "problem with line following blank line: %s" % next_line
                end_ind = term_ind + i
                term_lines = txt_mixin.txt_list(self.list[term_ind:end_ind])
                break

        ct_lines = term_lines.findallre('^Current Term:')
        assert len(ct_lines) == 1, "problem with Current Term lines: %s" %ct_lines
        ct_ind = ct_lines[0]
        ct_row_str = term_lines[ct_ind]
        ct_list = ct_row_str.split(self.delim)
        ct_gpa = float(ct_list[-1])

        self.cur_term_gpa = ct_gpa
        return ct_gpa


    def _get_completed_subject_lines(self, subject):
        subject_lines = self.get_subject_lines(subject)
        filt_lines = self.handle_lines_ending_in_E_and_I(subject_lines)
        completed_lines = self.filter_inprogress_courses(filt_lines)
        return completed_lines
        

    def find_ME_299_plus_gpa(self, debug=mod_debug):
        ## ME_lines = self.get_subject_lines('ME')
        ## filt_lines = self.handle_lines_ending_in_E_and_I(ME_lines)
        ## completed_ME = self.filter_inprogress_courses(filt_lines)
        if debug:
            print('ME 299+ GPA')
            #Pdb().set_trace()
        completed_ME = self._get_completed_subject_lines('ME')
        #me_gpa = self.gpa_from_list_of_lines(completed_ME)
        ME_299_plus_lines = self.filt_subject_lines_below_300(completed_ME)
        self.ME_299_plus_lines = ME_299_plus_lines
        debug = 1
        if debug:
            for line in ME_299_plus_lines:
                print line
                
        if len(ME_299_plus_lines) > 0:
            self.ME_299_plus_gpa = self.gpa_from_list_of_lines(self.ME_299_plus_lines)
        else:
            self.ME_299_plus_gpa = None
        return self.ME_299_plus_gpa


    def find_SOE_gpa(self, debug=mod_debug):
        if debug:
            print('SOE GPA')
        SOE_subjects = ['ME','CE','IME','CS','ECE']
        SOE_lines = []

        for subject in SOE_subjects:
            curlines = self._get_completed_subject_lines(subject)
            SOE_lines.extend(curlines)

        self.SOE_lines = SOE_lines
        self.SOE_gpa = self.gpa_from_list_of_lines(self.SOE_lines)
        return self.SOE_gpa
    

    def find_math_and_science_GPA(self, debug=mod_debug):
        if debug:
            print('math+science GPA')
        math_and_science_subjects = [ 'STAT','CHEM','PHYS','MATH']
        ms_lines = []

        for subject in math_and_science_subjects:
            curlines = self._get_completed_subject_lines(subject)
            ms_lines.extend(curlines)

        self.ms_lines = ms_lines
        self.ms_gpa = self.gpa_from_list_of_lines(self.ms_lines)
        return self.ms_gpa


    def prereq_check_482(self):
        ME_course_nums = self.get_course_nums('ME')

        prereqs = [350, 370, 380]

        num_missing = 0
        missing_list = []
        
        for prereq in prereqs:
            if prereq not in ME_course_nums:
                num_missing += 1
                missing_list.append(prereq)
                
        return missing_list


    def get_banner_id_from_filename(self):
        q = banner_id_pat.search(self.filename)
        self.id = q.group(1)
        
    
    def __init__(self, filename, delim='|', *args, **kwargs):
        txt_mixin.txt_file_with_list.__init__(self, filename, *args, **kwargs)
        self.delim = delim
        if os.path.exists(filename):
            self.get_banner_id_from_filename()



class batch_processor_for_transcripts(object):
    """This class exists to make it easy to batch pull the transcripts
    for all students enrolles in a course and then output a csv file
    with specific columns.  This class should be most likely used as a
    base class with classes being derived for specific courses."""
    def __init__(self, subject='ME', course='458', section='001', \
                 semester='201435', folder='transcripts', \
                 outdir=None, repull=False, reconvert=False):
        self.subject = subject
        self.course = course
        self.section = section
        self.semester = semester
        self.sem_int_str = semester[-2:]
        self.folder = folder
        self.outdir = outdir
        self.repull = repull
        self.reconvert = reconvert
        self.year = semester[0:4]

        if self.outdir is None:
            self.build_outdir()

        if not os.path.exists(self.outdir):
            rwkos.make_dirs_recrusive(self.outdir)


    def main(self):
        self.pull_classlist()
        self.classlist = classlist_parser(self.classlist_puller.pathout)
        self.ids = self.classlist.get_banner_ids()
        self.pull_all_trans(repull=self.repull)
        self.convert_all_html_to_txt(repull=self.repull)
        self.create_student_list()

    
    def build_outdir(self):
        base_dir = rwkos.FindFullPath('~/siue/classes')
        if self.subject.upper() != 'ME':
            course_str = '%s_%s' % (self.subject, self.course)
        else:
            course_str = self.course
        outdir = os.path.join(base_dir, course_str)
        #outdir = os.path.join(outdir, self.year)<-- pretty_sem will include the year
        pretty_sem = semester_str_to_pretty_str(self.semester)
        outdir = os.path.join(outdir, pretty_sem)
        outdir = os.path.join(outdir, self.folder)
        self.outdir = outdir
        return outdir


    def pull_classlist(self, repull=False):
        self.classlist_puller = classlist_puller(self.course, self.section, self.year, \
                                                 semester=self.sem_int_str, \
                                                 folder=self.folder, subject=self.subject)
        self.classlist_puller.build_filename()
        if repull or (not self.classlist_puller.exists()):
            self.classlist_puller.pull()


    def check_for_trans(self, id_str, ext='.html'):
        glob_pat = '*' + id_str + ext
        glob_pat = os.path.join(self.folder, glob_pat)
        curfiles = glob.glob(glob_pat)
        if len(curfiles) == 0:
            return False
        elif len(curfiles) == 1:
            return True
        else:
            raise ValueError, "found more than one match for " + glob_pat


    def check_for_txt_trans(self, id_str):
        return self.check_for_trans(id_str, ext='.txt')

    
    def pull_one_trans(self, id_str):
        curdir = os.getcwd()
        try:
            os.chdir(self.folder)
            cmd = 'transcript.sh ' + id_str
            os.system(cmd)
        finally:
            os.chdir(curdir)


    def pull_all_trans(self, repull=False):
        for cur_id in self.ids:
            if repull or (not self.check_for_trans(cur_id)):
                self.pull_one_trans(cur_id)


    def convert_one_html_to_txt(self, id_str):
        glob_pat = '*' + id_str + '.html'
        glob_pat = os.path.join(self.folder, glob_pat)
        curfiles = glob.glob(glob_pat)
        assert len(curfiles) == 1, "did not find exactly one match for " + glob_pat
        html_path = curfiles[0]
        html_parser = transcript_html_parser(html_path)
        html_parser.save(folder=self.folder)


    def convert_all_html_to_txt(self, repull=False):
        for cur_id in self.ids:
            if repull or (not self.check_for_txt_trans(cur_id)):
                self.convert_one_html_to_txt(cur_id)


    def create_one_student(self, id_str):
        glob_pat = '*' + id_str + '.txt'
        glob_pat = os.path.join(self.folder, glob_pat)
        curfiles = glob.glob(glob_pat)
        assert len(curfiles) == 1, "did not find exactly one match for " + glob_pat
        txt_path = curfiles[0]
        txt_parser = transcript_txt_parser(txt_path)
        return txt_parser


    def create_student_list(self):
        students = []
        ind_list = self.classlist.banner_ids.tolist()
        levels = self.classlist.get_levels()
        
        for cur_id in self.ids:
            cur_student = self.create_one_student(cur_id)
            ind = ind_list.index(cur_id)
            cur_student.level = levels[ind]
            students.append(cur_student)

        self.students = students


    def output_csv_list(self, list_of_tuples=[('Last Name', 'last_name'), \
                                              ('First Name', 'first_name'), \
                                              ('Banner ID','id'), \
                                              ('Level','level'), \
                                              ], \
                        prelim_methods=['break_name', 'get_major_and_dept']):
        """Create a nested list that can be dumped to a csv file.  Do
        by first calling prelim_methods on each student in
        self.students and then by retrieving the attr or calling the
        method for each tuple in list_of_tuples.  Each tuple should
        include (label, attr or method) as strings."""
        labels = [item[0] for item in list_of_tuples]
        big_list = []
        
        for student in self.students:
            currow = []
            for method_str in prelim_methods:
                method = getattr(student, method_str)
                method()

            for label, attr_str in list_of_tuples:
                attr = getattr(student, attr_str)
                if callable(attr):
                    value = attr()
                else:
                    value = attr
                currow.append(value)
                
            big_list.append(currow)
                    
        return big_list

def find_in_list(listin, lastname, firstname):
    """I am handling studnets who were already on probation separately
    from students who are new to probation.  So, I want to make sure
    the new list does not contain any old probation students.  So, I
    need to search the new list for old names."""

    for i, row in enumerate(listin):
        if (row[0] == lastname) and (row[1] == firstname):
            return i

    #this is technically needed, but I add it for clarity.  If you
    #have reached this point in the code, no match was found.
    return None


def pop_former_probation_names_from_new_list(newlist, oldlist):
    outlist = copy.copy(newlist)
    for row in oldlist:
        index = find_in_list(outlist, row[0], row[1])
        if index is not None:
            outlist.pop(index)

    return outlist

