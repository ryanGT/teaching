"""I am writing some utilities to work with the processing of class
lists and transcripts from Brad Noble's perl code."""
import txt_mixin
import os, re
import numpy
from numpy import array

from bs4 import BeautifulSoup

from IPython.core.debugger import Pdb

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

    
class classlist_parser(txt_mixin.txt_file_with_list):
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
        return self.get_col(2)
    
        
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



    

        
        
    def __init__(self, *args, **kwargs):
        txt_mixin.txt_file_with_list.__init__(self, *args, **kwargs)
        self.col_labels = ['#','Name','StudentID','Stat','Lvl','Grade','e-Mail Address']
        self.parse()


    def parse_names(self):
        self.name_strs = self.get_col(1)
        lastnames = []
        firstnames = []

        for item in self.name_strs:
            last, first = parse_one_name(item)
            lastnames.append(last)
            firstnames.append(first)

        self.lastnames = lastnames
        self.firstnames = firstnames
        
        
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
    def save(self, txt_path=None):
        if txt_path is None:
            txt_path = self.txt_filename

        txt_mixin.dump(txt_path, self.txt_list)
        
        
    def __init__(self, filename):
        self.html_filename = filename
        fno, ext = os.path.splitext(self.html_filename)
        self.txt_filename = fno + '.txt'

        self.txt_list = transcript_html_to_txt_list(self.html_filename)


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
        gpa = float(num)/float(den)

        return gpa
            


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
        return gpa


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
    
    
    def __init__(self, filename, delim='|', *args, **kwargs):
        txt_mixin.txt_file_with_list.__init__(self, filename, *args, **kwargs)
        self.delim = delim
        
