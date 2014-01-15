"""I am writing some utilities to work with the processing of class
lists and transcripts from Brad Noble's perl code."""
import txt_mixin
import os, re
import numpy
from numpy import array

from bs4 import BeautifulSoup
    
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



def process_one_table_row(row_list, delim='|'):
    rowstr = ''
    for td in row_list:
        text = None
        if td.find(text=True):
            text = ''.join(td.find(text=True))
            text = text.replace('&nbsp',' ')
            text = text.replace(u'\xa0', u' ')
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


class transcript_txt_parser(txt_mixin.txt_file_with_list):
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


    def IME_106_report(self):
        """Generate a report to check if a student is a declared
        engineering major or could be so."""
        name = self.get_name()
        listout = [name]
        college_lines = self.get_regexp_matches('^College *:')
        listout.extend(college_lines)
        major_lines = self.get_regexp_matches('^Major')
        listout.extend(major_lines)
        listout.append('')
        
        transfer_ind = self.list.findallre('^TRANSFER CREDIT ACCEPTED BY INSTITUTION')[0]
        siue_ind = self.list.findallre('^INSTITUTION CREDIT')[0]
        inprogress_ind = self.list.findallre('^COURSES IN PROGRESS')[0]
        math_inds = self.list.findallre('^MATH')
        math_inds.sort()
        if numpy.min(math_inds) < siue_ind:
            listout.append('TRANSFER Math Course(s):')
            listout.append('='*30)
            listout.append('')
        
            for ind in math_inds:
                if ind < siue_ind:
                    listout.append(self.list[ind])

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
    
    
    def __init__(self, filename, delim='|', *args, **kwargs):
        txt_mixin.txt_file_with_list.__init__(self, filename, *args, **kwargs)
        self.delim = delim
        
