import re

import os, subprocess, re, copy
#import txt_mixin

#from IPython.core.debugger import Pdb

#from mybanner import MYSID, MYPIN
USERAGENT="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0"
ACCEPTSTR="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
cookiepath = 'cookies.txt'

p_course = re.compile('<a.*?>(.*?) - (\d{5}) - ([A-Z]+) (\d{3}[A-Z]*) - (.*)</a>')


# extra wget flags with no values:
flags = ['no-check-certificate','keep-session-cookies']

# create dictionary of default options
default_opts = {'user-agent': USERAGENT, \
                'load-cookies':cookiepath, \
                'save-cookies':cookiepath, \
                'accept':ACCEPTSTR, \
                }






# misc banner utils
def assemble_post_data(data_dict):
    outstr = ''
    for key, val in data_dict.iteritems():
        if outstr:
            #include & if string is not empty, i.e. not first option
            outstr += '&'
        outstr += "%s=%s" % (key,val)

    final_out = '--post-data="%s"' % outstr
    return final_out


def make_options_list(opt_dict):
    """append options in opt_dict to cmdin using ' --key=value'"""
    opt_list = []
    for key, val in opt_dict.iteritems():
        #add quotes to val if needed
        if val[0] != '"':
            val = '"%s"' % val
        opt_list.append('--%s=%s' % (key, val))

    return opt_list


def _build_cmd(url, referer=None, post_params=None):
    """Build the wget command string that will be passed to
    subprocess.  post_params can be either a dictionary or a
    preformatted string.  If it is a string, it must include
    --post_params=
    post_params and referer are both optional."""
    #cmd = 'wget'
    all_args = ['wget']
    for flag in flags:
        all_args.append('--'+flag)
    list1 = make_options_list(default_opts)
    all_args.extend(list1)
    if referer:
        list2 = make_options_list({'referer':referer})
        all_args.extend(list2)

    if post_params:
        if type(post_params) == dict:
            post_str = assemble_post_data(post_params)
        else:
            post_str = post_params

        all_args.append(post_str)

    all_args.extend(['-O -', url])
    cmd = ' '.join(all_args)
    return cmd


def call_wget(url, referer=None, post_params=''):
    cmd = _build_cmd(url, referer=referer, post_params=post_params)
    p = subprocess.Popen(cmd, shell=True, \
                         stdout=subprocess.PIPE, \
                         stderr=subprocess.PIPE)
    output, errors = p.communicate()
    return output, errors


#note that term is 6 digits and a pure % converts to '%25'
def build_class_search_str(term, subj, course=''):
    post_str = '--post-data="term_in=$TERM&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj=$SUBJ&sel_crse=$CRSE&sel_title=&sel_schd=%25&sel_insm=%25&sel_from_cred=&sel_to_cred=&sel_camp=%25&sel_levl=%25&sel_ptrm=%25&sel_instr=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a"'
    out_str = post_str.replace('$TERM',term)
    out_str = out_str.replace('$SUBJ',subj)
    out_str = out_str.replace('$CRSE',course)
    return out_str

def extract_matching_courses(htmlstr, subj, course=''):
    """split the string htmlstr into a list of lines (split at \n)
    then find all lines that match '- subs course'"""

    outlines = []
    htmllines = htmlstr.split('\n')#<-- this might be bad if the html had different line breaks
    search_pat = '- %s %s' % (subj, course)
    for line in htmllines:
        if line.find(search_pat) > -1:
            outlines.append(line)

    return outlines


class banner_course(object):
    def __init__(self, htmlline):
        """create a course based on an html line that matches the
        regexp pattern"""
        reg_exp_match = p_course.search(htmlline)
        assert reg_exp_match is not None, "problem with reg_exp_match"
        self.title = reg_exp_match.group(1)
        self.crn = reg_exp_match.group(2)
        self.subject = reg_exp_match.group(3)
        self.course = reg_exp_match.group(4)
        self.section = reg_exp_match.group(5)

    def __repr__(self):
        attr_list = ['subject','course','section','crn']
        outstr = ''
        for attr in attr_list:
            if hasattr(self, attr):
                if outstr:
                    outstr += ' '#leading space if outstr is already non-blank
                outstr += str(getattr(self, attr))

        if hasattr(self, 'title'):
            outstr += ' - ' + str(getattr(self, attr))

        return outstr


    
## <table  CLASS="datadisplaytable" summary="This table displays a list of students registered for the course; summary information about each student is provided." WIDTH="100%"><caption class="captiontext">Summary Class List</caption>
## <tr>
## <th CLASS="ddheader" scope="col" >Record<br />Number</th>
## <th CLASS="ddheader" scope="col" >Student Name</th>
## <th CLASS="ddheader" scope="col" ><ACRONYM title = "Identification Number">ID</ACRONYM></th>
## <th CLASS="ddheader" scope="col" ><ABBR title = "Registration Status">Reg Status</ABBR></th>
## <th CLASS="ddheader" scope="col" >Level</th>
## <th CLASS="ddheader" scope="col" >Credits</th>
## <th CLASS="ddheader" scope="col" >Grade Detail</th>
## <td CLASS="dddead">&nbsp;</td>
## </tr>


## <tr>
## <td CLASS="dddefault">1</td>
## <td CLASS="dddefault"><SPAN class="fieldmediumtext"><a href="/pls/BANPROD/bwlkosad.P_FacSelectAtypView?xyz=NTAyMTg4" onMouseOver="window.status='Student Information';  return true" onFocus="window.status='Student Information';  return true" onMouseOut="window.status='';  return true"onBlur="window.status='';  return true">Brocksieck, Adam J.</a> </SPAN></td>
## <td CLASS="dddefault"><SPAN class="fieldmediumtext">800481860</SPAN></td>
## <td CLASS="dddefault"><SPAN class="fieldmediumtext">Registered via Web</SPAN></td>
## <td CLASS="dddefault"><SPAN class="fieldmediumtext">Undergraduate</SPAN></td>
## <td CLASS="dddefault"><SPAN class="fieldmediumtext">    2.000</SPAN></td>
## <td CLASS="dddead">&nbsp;</td>
## <td CLASS="dddefault"><SPAN class="fieldmediumtext"><a href="mailto:abrocks@siue.edu"    target="Adam J. Brocksieck" ><img src="/wtlgifs/web_email.gif" align="middle" alt="E-mail" CLASS="headerImg" TITLE="E-mail"  NAME="web_email" HSPACE=0 VSPACE=0 BORDER=0 HEIGHT=28 WIDTH=28 /></a></SPAN></td>
## </tr>

summary_pat = re.compile('<table .*>Summary Class List<')
detail_pat = re.compile('<table .*>Detail Class List<')
name_pat = re.compile(".*\'Student Information\'.*>(.*?)</a>")
id_pat = re.compile(">(G\d{8})<")
generic_data_pat = re.compile('<td CLASS=".*"><SPAN class=".*">(.*?)</SPAN></td>')
email_pat = re.compile('href="mailto:(.*?)"')
record_number_pat = re.compile('<th .*?>Record<br />Number</th>')
email_class_pat = re.compile('<a.*?>Email class</a>')
th_pat = re.compile('<th .*?>(.*?)</th>')
td_pat = re.compile('<td .*?>(.*?)</td>')



class student(object):
    def __init__(self, linesin):
        self.linesin = linesin
        self.next_ind = 0
        self.N = len(self.linesin)
        self.csv_attrs = attrs = ['lastname', 'firstname','id','reg_method','level', \
                                  'credits','email']
        self.parse_lines()
        

    def find_next_re(self, re_pat):
        for i in range(self.next_ind, self.N):
            curline = self.linesin[i]
            res = re_pat.search(curline)
            if res:
                self.next_ind = i+1
                return res


    def assign_regexp_group_to_attr(self, reg_res, attr, group=1):
        val = reg_res.group(group).strip()
        setattr(self, attr, val)
        

    def parse_lines(self):
        # first find ".*'Student Information'.*>([.*?])</a>"
        # then find ">(\d{9})<"
        # grab data from these lines:
        #   <td CLASS="dddefault"><SPAN class="fieldmediumtext">Registered via Web</SPAN></td> (3 lines)
        # pull email from here: href="mailto:mzdanow@siue.edu"

        # go through regexp pat in order and assign group(1) to self.attr:
        pat_attr_list = [(name_pat, 'raw_name'), \
                         (id_pat, 'id'), \
                         (generic_data_pat, 'reg_method'), \
                         (generic_data_pat, 'level'), \
                         (generic_data_pat, 'credits'), \
                         (email_pat, 'email')]

        for pat, attr in pat_attr_list:
            reg_res = self.find_next_re(pat)
            self.assign_regexp_group_to_attr(reg_res, attr)


    def __repr__(self):
        attr_list = ['raw_name','id','reg_method','level','credits','email']
        outstr = ''
        for attr in attr_list:
            if hasattr(self, attr):
                outstr += '%s: %s\n' % (attr, getattr(self, attr))

        return outstr


    def split_name(self):
        """Assume raw_name is 'Last, First MI. but MI. is optional.
        This could be a bad assumption for international students.  I
        will dump raw_name into the csv and not worry abou it."""
        mylist = self.raw_name.split(',')
        last = mylist[0].strip()
        rest = mylist[1].strip()
        assert len(mylist) == 2, "more than one comma in name: %s" % self.raw_name

        if rest.find(' ') > -1:
            first, mi = rest.split(' ',1)
        else:
            first = rest

        first = first.strip()

        self.lastname = last
        self.firstname = first


    def email_csv(self):
        raw_str = '"%s"' % self.raw_name
        email  = getattr(self, 'email')
        mylist = [raw_str, email]
        csv_str = ','.join(mylist)
        return csv_str

        
    def to_csv(self):
        """spit out raw_name, lastname, firstname,
        'id','reg_method','level','credits','email'"""
        self.split_name()
        #quote raw name first because it likely contains a comma
        raw_str = '"%s"' % self.raw_name
        mylist = [raw_str]


        for attr in self.csv_attrs:
            if hasattr(self, attr):
                val  = getattr(self, attr)
            else:
                val = ''
            mylist.append(val)

        csv_str = ','.join(mylist)

        return csv_str



class detail_student(student):
    def __init__(self, *args, **kwargs):
        student.__init__(self, *args, **kwargs)
        self.csv_attrs = ['lastname', 'firstname','id','reg_method','level', \
                          'email', \
                          'admit_term', \
                          'admit_type', \
                          'catalog_term', \
                          'college', \
                          'level', \
                          'major', \
                          'major_concentration', \
                          'program', \
                          ]
        
    def detail_dict_to_attrs(self):
        for key, val in self.detail_dict.items():
            clean_key = key.replace(' ','_')
            clean_key = clean_key.lower()
            setattr(self, clean_key, val)

            
    def parse_lines(self):
        pat_attr_list = [(name_pat, 'raw_name'), \
                 (id_pat, 'id'), \
                 (td_pat, 'reg_method'), \
                 (email_pat, 'email')]

        for pat, attr in pat_attr_list:
            reg_res = self.find_next_re(pat)
            self.assign_regexp_group_to_attr(reg_res, attr)


        # ? do I just pop th and td pairs or am I extracting specific information?
        th_list = ['Level','Program','Admit Term', \
                   'Admit Type','Catalog Term','College','Major', \
                   'Major Concentration']

        detail_dict = {}
        th_gen_pat = '<th .*?>%s</th>'

        detail_ind = copy.copy(self.next_ind)
        
        for key in th_list:
            search_key = key + ':'
            th_str = th_gen_pat % search_key
            cur_pat = re.compile(th_str)

            # I don't want to assume the key are in the right order, so
            # I am not using self.find_next_re
            for i in range(detail_ind,self.N):
                curline = self.linesin[i]
                res = cur_pat.search(curline)
                if res:
                    # the next list should contain the table data info we want
                    next_line = self.linesin[i+1]
                    td_res = td_pat.search(next_line)
                    if td_res:
                        data = td_res.group(1)
                        detail_dict[key] = data
                    ## else:
                    ##     print('problem with next line for key %s' % key)
                    ##     print(next_line)
                    ##     Pdb().set_trace()

                    break


        self.detail_dict = detail_dict
        self.detail_dict_to_attrs()
        
        # <th > and <td > within the same row clearly go together
        # <td >&nbsp;</td> can be thrown out
        #  - will <th > it its own row always match up with <td > in next row?
        #  - do I just match <th > and <td > pairs without caring about the row?
        #this should take us to the end of email and we are ready to deal with these things:
        #
        #</tr>
        #<tr>
        #<td colspan="4" CLASS="dddead">&nbsp;</td>
        #</tr>
        #<tr>
        #<th colspan="4" CLASS="ddlabel" scope="row" >Current Program</th>
        #</tr>
        #<tr>
        #<td colspan="4" CLASS="dddefault">Bachelor of Sci in Engineering</td>
        #</tr>
        #<tr>
        #<th colspan="2" CLASS="ddlabel" scope="row" >Level:</th>
        #<td colspan="2" CLASS="dddefault">Undergraduate</td>
        #</tr>
        #<tr>
        #<th colspan="2" CLASS="ddlabel" scope="row" >Program:</th>
        #<td colspan="2" CLASS="dddefault">Mechanical Engineering-BSE</td>
        #</tr>
        #<tr>
        #<th colspan="2" CLASS="ddlabel" scope="row" >Admit Term:</th>
        #<td colspan="2" CLASS="dddefault">Fall 2015</td>
        #</tr>
        #<tr>
        #<th colspan="2" CLASS="ddlabel" scope="row" >Admit Type:</th>
        #<td colspan="2" CLASS="dddefault">High School Applicant</td>
        #</tr>
        #<tr>
        #<th colspan="2" CLASS="ddlabel" scope="row" >Catalog Term:</th>
        #<td colspan="2" CLASS="dddefault">Fall 2015</td>
        #</tr>
        #<tr>
        #<th colspan="2" CLASS="ddlabel" scope="row" >College:</th>
        #<td colspan="2" CLASS="dddefault">Padnos Col of Egr & Computing</td>
        #</tr>
        #<tr>
        #<th colspan="2" CLASS="ddlabel" scope="row" >Major:</th>
        #<td colspan="2" CLASS="dddefault">Mechanical Engineering</td>
        #</tr>
        #<tr>
        #<td CLASS="ddseparator">&nbsp;</td>
        #</tr>



def verify_row(rows):
    """Verify that a group of rows contains a student's information.
    The first row in the summary table should fail."""
    row_str = '\n'.join(rows)
    if row_str.find("'Student Information'") > -1:
        return True
    else:
        return False

        
class html_class_list_parser(object):
    def __init__(self, htmlstr):
        self.htmlstr = htmlstr
        self.htmllist = htmlstr.split('\n')
        self.table_start_pat = summary_pat
        self.next_ind = -1
        self.N = len(self.htmllist)
        self.students = []
        self.student_lines = []
        self.csv_labels = ['raw_name','lastname','firstname','id',\
                           'reg_method','level','credits','email']
        #self.parse()
        

    def find_class_list_table(self):
        found = False
        for i, line in enumerate(self.htmllist):
            if self.table_start_pat.search(line):
                self.next_ind = i+1
                found = True
                break

        return found


    def find_next(self, search_str, start_ind=None):
        if start_ind is None:
            start_ind = self.next_ind

        found_ind = -1
        
        for i in range(start_ind, self.N):
            if self.htmllist[i].find(search_str) > -1:
                found_ind = i
                break

        return found_ind


    def find_next_re(self, re_pat, start_ind=None):
        if start_ind is None:
            start_ind = self.next_ind

        found_ind = -1

        for i in range(start_ind, self.N):
            res = re_pat.search(self.htmllist[i])
            if res:
                self.next_ind = i+1
                found_ind = i
                break

        return found_ind
    

    def find_next_row(self):
        start_ind = self.find_next('<tr>')
        if start_ind == -1:
            # we are out of students
            return None
        
        end_ind = self.find_next('</tr>', start_ind)
        if end_ind > -1:
            # we found a row, increment next_ind
            self.next_ind = end_ind+1
            
        return self.htmllist[start_ind:self.next_ind]
    

    def find_next_student_lines(self):
        """search for the next <tr> and </tr> pair and verify they
        correspond to a student"""
        if self.next_ind == -1:
            #we have called find_class_list_table yet or it wasn't found
            found = self.find_class_list_table()
            assert found, "problem finding class list table"

        # - find next <tr> and then the </tr> after that
        # - grab the lines in between <tr> and </tr>
        # - pass them to the student class for parsing
        row_lines = self.find_next_row()
        if not row_lines:
            return None
        
        test = verify_row(row_lines)

        if not test:
            return None

        return row_lines
            

    def parse(self):
        self.find_class_list_table()
        mybool = True
        # the first time should fail;
        # how do we know when to stop searching?
        i = 0
        while mybool:
            i += 1
            next_lines = self.find_next_student_lines()
            if next_lines is not None:
                self.student_lines.append(next_lines)
            elif i > 1 and next_lines is None:
                mybool = False


    def make_students(self):
        for curlist in self.student_lines:
            curstudent = student(curlist)
            self.students.append(curstudent)
        

    def to_csv_list(self):
        label_str = ','.join(self.csv_labels)
        csv_list = [label_str]

        for student in self.students:
            csv_str = student.to_csv()
            csv_list.append(csv_str)

        return csv_list


    def to_email_list(self):
        labels = ['name','email']
        label_str = ','.join(labels)
        csv_list = [label_str]

        for student in self.students:
            csv_str = student.email_csv()
            csv_list.append(csv_str)

        return csv_list
            

    def csv_list_to_path(self, csv_list, filepath):
        #add a newline to each row
        csv_w_newlines = [item + '\n' for item in csv_list]
        f = open(filepath, 'w')
        f.writelines(csv_w_newlines)
        f.close()

        
    def save(self, filepath):
        csv_list = self.to_csv_list()
        self.csv_list_to_path(csv_list, filepath)
        

    def save_email_csv(self, filepath):
        csv_list = self.to_email_list()
        self.csv_list_to_path(csv_list, filepath)
                          


class detail_class_list_parser(html_class_list_parser):
    def __init__(self, *args, **kwargs):
        html_class_list_parser.__init__(self, *args, **kwargs)
        self.table_start_pat = detail_pat
        

    def find_next_row(self):
        """A summary class list has one student per row; a detail
        class list is more complicated.  The current student end where the next student
        begins and each student spans mulitple rows.  Find the start of the next
        student and then back up to the previous </tr>"""
        start_ind = self.find_next_re(name_pat)
        if start_ind == -1:
            # we are out of students
            return None

        # each student starts with this label
        # <th CLASS="ddheader" scope="col" >Record<br />Number</th>
        
        end_ind = self.find_next_re(record_number_pat, start_ind) -1
        
        if end_ind > -1:
            # we found a row, increment next_ind
            self.next_ind = end_ind
        else:
            # we are at the last student, end at Email Class    
            end_ind = self.find_next_re(email_class_pat, start_ind) -1
        return self.htmllist[start_ind:self.next_ind]



    def make_students(self):
        for curlist in self.student_lines:
            curstudent = detail_student(curlist)
            self.students.append(curstudent)
            
        self.csv_labels = ['raw_name'] + curstudent.csv_attrs


if __name__ == '__main__':
    f = open('debug.html','rb')
    #add this stuff to class_puller.py and move any universal
    #functions from class_puller.py to this module
    myhtml = f.read()
    f.close()
    from IPython.core.debugger import Pdb
    #Pdb().set_trace()
    myparser = html_class_list_parser(myhtml)
    myparser.parse()
    myparser.make_students()
    csv_list = myparser.to_csv_list()
    myparser.save('debug.csv')

        
## def parse_summary_class_list(htmlstr):
##     """Approach:

##        1. find the table that contains '>Summary Class List<'
##        2. ignore the first row
##        3. each subsequent row contains the data for one student
##        4. extract each batch for rows and parse them as one student
##        """
