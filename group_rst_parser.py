"""This is a second attempt at a module for compiling and emailing
group grades from feedback typed into an rst form.  This module will
generalize presentation_rst_parser.py so that the classes can be used
for emailing and compiling grades on the written proposals."""

import txt_mixin, spreadsheet, rst_creator, rwkos
import re, os
import gmail_smtp
reload(gmail_smtp)
from numpy import array, where

from scipy import mean

from IPython.Debugger import Pdb

grade_pat = re.compile(':grade:`(.*)`')
timing_pat = re.compile('^Tim(ing|e)[: ]*$')
notes_pat = re.compile('^Notes*[: ]*$')

import copy
reload(spreadsheet)

mysig = """

--
Ryan Krauss, Ph.D.
Assistant Professor
Mechanical Engineering
Southern Illinois University Edwardsville"""


def clean_list(listin):
    """Remove empty lines at the beginning and end of a list."""
    listout = copy.copy(listin)
    while (len(listout) > 0) and (not listout[0]):
        listout.pop(0)
    while (len(listout) > 0) and (not listout[-1]):
        listout.pop()
    return listout


mysecdec = rst_creator.rst_section_level_3()
subsec_dec = rst_creator.rst_section_dec()

class section(txt_mixin.txt_list):
    def __init__(self, raw_list, subre=None, subclass=None, \
                 has_title=True):
        #print('raw_list=')
        #print('\n'.join(raw_list))
        self.subweights = None
        if has_title:
            self.title = raw_list.pop(0)
            self.dec_line = raw_list.pop(0)
        else:
            self.title = None
            self.dec_line = None
        clean_content = clean_list(raw_list)
        self.content = txt_mixin.txt_list(clean_content)
        grade_inds = self.content.findall(':grade:`')
        if len(grade_inds) > 0:
            grades = None
            for ind in grade_inds:
                grade_line = self.content[ind]
                q = grade_pat.search(grade_line)
                cur_grade = float(q.group(1))
                if grades is None:
                    grades = [cur_grade]
                else:
                    grades.append(cur_grade)
            self.grade = mean(grades)

        self.subre = subre
        self.subclass = subclass
        if (subre is not None) and (subclass is not None):
            self.break_into_sections()


    def break_into_sections(self):
        inds = self.content.findallre(self.subre)
        if len(inds) == 0:
            return
        inds2 = [item-1 for item in inds]
        inds2.append(None)
        self.raw_sec_list = None
        prevind = inds2.pop(0)
        self.header = self.content[0:prevind]
        for ind in inds2:
            curlist = self.content[prevind:ind]
            if self.raw_sec_list is None:
                self.raw_sec_list = [curlist]
            else:
                self.raw_sec_list.append(curlist)
            prevind = ind
        self.sec_list = None

        for curlist in self.raw_sec_list:
            cur_sec = self.subclass(curlist)
            if self.sec_list is None:
                self.sec_list = [cur_sec]
            else:
                self.sec_list.append(cur_sec)

    def find_section(self, title):
        for sec in self.sec_list:
            if sec.title == title:
                return sec

    def calc_grade(self):
        if self.subweights:
            self.total_weight = 0.0
            self.weighted_total = 0.0
            for title, weight in self.subweights.iteritems():
                sec = self.find_section(title)
                self.total_weight += weight
                self.weighted_total += sec.grade * weight
            self.grade = self.weighted_total/self.total_weight
        
    def __repr__(self):
        outstr = self.title+'\n' + \
                 self.dec_line +'\n'+ \
                 '\n'.join(self.content)
        return outstr


class section_level_2(section):
    def __init__(self, raw_list, subre=None, subclass=None):
        section.__init__(self, raw_list, subre=subre, \
                         subclass=subclass)

class section_level_1(section):
    def __init__(self, raw_list, subre='^\++$', \
                 subclass=section_level_2):
        section.__init__(self, raw_list, subre=subre, \
                         subclass=subclass)

    def get_grades(self):
        self.calc_grade()
        self.grade_list = None
        for section in self.sec_list:
            curgrade = section.grade
            if self.grade_list is None:
                self.grade_list = [curgrade]
            else:
                self.grade_list.append(curgrade)
        self.grade_list.append(self.grade)
        return self.grade_list


    def get_labels(self):
        self.labels = None
        for section in self.sec_list:
            curtitle = section.title
            if self.labels is None:
                self.labels = [curtitle]
            else:
                self.labels.append(curtitle)
        self.labels.append(self.title)
        return self.labels
    
    def create_rst(self):
        rst_out = [self.title]
        rst_out.append(self.dec_line)
        rst_out.extend(self.content)
        self.rst = rst_out
        return self.rst
        

class lit_review(section_level_1):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.05

    def get_grades(self):
        self.grade_list = [self.grade]
        return self.grade_list

    def get_labels(self):
        self.labels = [self.title]
        return self.labels


class default_section_no_children(section_level_1):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 1.0

    def get_grades(self):
        self.grade_list = [self.grade]
        return self.grade_list

    def get_labels(self):
        self.labels = [self.title]
        return self.labels


class contemp_issues(lit_review):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.05

class extra_credit(lit_review):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1

class penalty(extra_credit):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1    

    def create_rst(self):
        rst_out = [self.title]
        rst_out.append(self.dec_line)
        rst_out.append('')
        grade_str = '%0.2g' % self.grade + '%'
        grade_line = ':grade:`%s`' % grade_str
        rst_out.append(grade_line)
        self.rst = rst_out
        return self.rst


    
class quick_read(section_level_1):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.15
        self.subweights = {'Abstract':1.0, \
                           'Introduction':1.0, \
                           'Conclusion':1.0, \
                           'Organization':0.2}

    def create_rst(self):
        section_level_1.create_rst(self)
        self.rst.append('')
        sublist = subsec_dec('Weighted Average: '+self.title)
        self.rst.extend(sublist)
        self.rst.append(':grade:`%0.3g`' % self.grade)
        return self.rst

        
class slow_read(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.25
        self.subweights = {'Problem Statement and Formulation': 1.0, \
                           'Organization and Flow': 0.5, \
                           'Clarity and Tone': 1.0, \
                           'Format/Style': 1.0, \
                           'Required Sections': 0.2, \
                           'Technical Language': 1.0, \
                           'Grammar and Spelling': 1.0}


class content_sec(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.5
        self.subweights = {'Persuasiveness': 1.0, \
                           'Design Strategy': 1.0, \
                           'Analysis': 1.0, \
                           'Background Research': 1.0, \
                           'Constraints': 0.8 , \
                           'Computers and Software': 0.8 , \
                           'Timeline': 0.8 , \
                           'Budget': 0.8}


class member(object):
    def __init__(self, lastname, firstname, email):
        self.lastname = lastname
        self.firstname = firstname
        self.email = email
        
    
class speaker(object):
    """Class for getting feedback to an individual speaker in a group
    presentation."""
    def __init__(self, linesin, parent):
        self.parent = parent
        mylines = copy.copy(linesin)
        self.line1 = mylines.pop(0)
        self.dec_line = mylines.pop(0)
        temp, name = self.line1.split(':',1)
        self.name = name.strip()
        self.content = mylines
        self.get_email()

    def get_email(self):
        try:
            me = self.parent.members[self.name]
        except ValueError:
            print('could not find self.name in parent.firstnames')
            print('    self.name=' + str(self.name))
            print('    parent.firstnames=' + str(self.parent.firstnames))
            print('    parent.lastnames=' + str(self.parent.lastnames))
        self.email = me.email

    def get_rst_name(self):
        poutpath = self.parent.outpath
        pne, ext = os.path.splitext(poutpath)
        clean_name = self.name.replace(' ','_')
        clean_name = clean_name.replace('.','')
        self.outpath = pne + '_' + clean_name + ext
        
    def build_rst(self):
        self.rst = copy.copy(self.parent.header)
        self.rst.append('')
        self.rst.append(self.line1)
        self.rst.append(self.dec_line)
        self.rst.extend(self.content)

    def set_pdfpath(self):
        pne, ext = os.path.splitext(self.outpath)
        self.pdfpath = pne+'.pdf'

    def save_rst(self):
        self.get_rst_name()
        txt_mixin.dump(self.outpath, self.rst)

    def run_rst(self):
        cmd = 'rst2latex_rwk.py -c 2 -n 0 ' + self.outpath
        os.system(cmd)
        self.set_pdfpath()

    def build_run_and_save_rst(self):
        self.build_rst()
        self.save_rst()
        self.run_rst()
        
    def send_email(self, subject, debug=0):
        if debug:
            email = 'ryanlists@gmail.com'
        else:
            email = self.email
        #addresses = ['ryanwkrauss@gmail.com', 'ryanlists@gmail.com', 'ryanwkrauss@att.net']
        body = self.name + ', \n\n' 
        body += "The attached pdf contains feedback on your individual speaking and delivery grade."
        body += mysig
        gmail_smtp.sendMail(email, subject, body, self.pdfpath)


class group(object):
    def __init__(self, group_name, group_list=None, email_list=None, \
                 alts={}):
        self.group_name = group_name
        self.group_list = group_list
        self.email_list = email_list
        self.alts = alts
        if (group_list is not None) and (email_list is not None):
            self.find_members()


    def clean_firstname(self, firstin):
        out = firstin.split(' ',1)
        first = out[0]
        return first


    def get_first_and_last_names(self):
        lastnames, firstnames = self.group_list.get_names(self.group_name)
        self.lastnames = lastnames
        self.firstnames = firstnames


    def find_alt_firstnames(self):
        self.alt_firstnames = copy.copy(self.firstnames)
        for n, lastname in enumerate(self.lastnames):
            if self.alts.has_key(lastname):
                self.alt_firstnames[n] = self.alts[lastname]
        
        
    def build_names_tuples(self):
        if not hasattr(self, 'lastnames'):
            self.get_first_and_last_names()
        names = []
        for first, last in zip(self.firstnames, self.lastnames):
            curtup = (first, last)
            names.append(curtup)
        self.names = names
            
    
    def find_members(self):
        self.get_first_and_last_names()
        self.find_alt_firstnames()
        self.append_initials_to_firstnames()
        members = None
        emails = []

        for last, first in zip(self.lastnames, self.alt_firstnames):
            try:
                email = self.email_list.get_email(last)
            except AssertionError:
                email = self.email_list.get_email(last, first)
            emails.append(email)
            curmember = member(last, first, email)
            if members is None:
                members = {first:curmember}
            else:
                members[first] = curmember
        self.members = members
        self.emails = emails#self.email_list.get_emails(lastnames)
        return self.emails


    def append_initials_to_firstnames(self):
        """Fix self.firstnames by appending a last initial if
        necessary."""
        self.firstnames = txt_mixin.txt_list(self.firstnames)
        self.raw_firstnames = copy.copy(self.firstnames)
        N = len(self.firstnames)
        for i in range(N):
            first = self.firstnames[i]
            inds = self.firstnames.findall(first)
            if len(inds) > 1:
                for j in inds:
                    first = self.firstnames[j]
                    last = self.lastnames[j]
                    first += ' ' + last[0] + '.'
                    self.firstnames[j] = first



class group_with_team_ratings(group):
    def get_scores_from_students(self):
        N = len(self.students)
        nr, nc = self.students[0].scores.shape
        scores = zeros((N,nr,nc))
        for i, student in enumerate(self.students):
            scores[i,:,:] = student.scores
        self.scores = scores


    def calc_aves(self):
        self.ave_scores = self.scores.mean(axis=0)#the average scores
            #for each student
        self.team_cat_ave_scores = self.ave_scores.mean(axis=-1)#team
            #average
            #for
            #each
            #category
        self.team_overall_ave = self.team_cat_ave_scores.mean()#overall
            #team
            #average

    def calc_category_ratios(self):
        for student in self.students:
            student.get_my_category_aves()

    def fix_team_factors(self):
        #algorithm modified 4/29/11
        #Pdb().set_trace()
        above_inds = where(self.team_factors >= 1.1)[0]
        m = float(len(above_inds))
        rest_inds = where(self.team_factors < 1.1)[0]
        n = float(len(rest_inds))
        self.team_factors[above_inds] = 1.1

        filt_below = self.team_factors[rest_inds]
        old_ave = filt_below.mean()
        new_ave = (n+m-1.1*m)/n
        scale_factor = new_ave/old_ave
        self.team_factors[rest_inds] *= scale_factor

        ave1 = self.team_factors.mean()

        eps = 1e-4
        assert abs(ave1-1.0) < eps, "Problem with intermediate average after clipping at 1.1 and scaling up.  %s, ave1 = %0.4g" % (self.group_name, ave1)

        aves_below = where(self.team_factors < 0.8)[0]
        self.team_factors[aves_below] = 0.8

        self.team_factor_ave = self.team_factors.mean()

        N = len(self.names)
        self.team_factor_ave_vect = array([self.team_factor_ave]*N)
        assert self.team_factor_ave > 0.92, "Team with really low average: %s: %0.4g" % (self.group_name, self.team_factor_ave)
        assert self.team_factor_ave < 1.03, "Team with really high average: %s: %0.4g" % (self.group_name, self.team_factor_ave)

        for student, tf in zip(self.students, self.team_factors):
            student.team_factor = tf


    def build_name_str(self):
        N = len(self.students)
        if N == 1:
            self.name_str = ' '.join(self.names[0])
        else:
            name_str = ''
            for n, pair in enumerate(self.names):
                if n > 0:
                    name_str +=', '
                if n == (N-1):
                    name_str += 'and '
                name_str += pair[0] + ' ' + pair[1]
            self.name_str = name_str


    def calc_overall_ave(self):
        self.means = array([student.mean for student in self.students])
        self.overall_mean = self.means.mean()


    def find_student(self, search_student):
        found = 0
        for student in self.students:
            if student.firstname == search_student.firstname and \
                   student.lastname == search_student.lastname:
                found = 1
                return student
        assert found == 1, "Did not find student: \n" + \
               search_student.firstname + ' ' +search_student.lastname


    def get_data_for_student(self, search_student):
        student_scores = None
        for student in self.students:
            cur_scores = student.find_col(search_student)
            if student_scores is None:
                student_scores = [cur_scores]
            else:
                student_scores.append(cur_scores)
        mystudent = self.find_student(search_student)
        mystudent.myscores = array(student_scores).T
        mystudent.calc_team_factor()


    def get_student_scores(self):
        for student in self.students:
            self.get_data_for_student(student)


    def copy_team_factors_to_raw(self):
        self.raw_team_factors = copy.copy(self.team_factors)


    def calc_team_factor_average(self):
        team_factors = None
        for student in self.students:
            tf = student.team_factor
            if team_factors is None:
                team_factors = [tf]
            else:
                team_factors.append(tf)
        team_factors = array(team_factors)
        self.team_factors = team_factors


    def check_team_factors_ave(self):
        if not hasattr(self, 'team_factors'):
            self.calc_team_factor_average()
            
        self.team_factor_ave = self.team_factors.mean()
        if abs(1.0 - self.team_factor_ave) > 1e-7:
            print('possible problem with self.team_factor_ave: ' + \
                  str(self.team_factor_ave))
        if self.team_factors.max() > 1.1:
            print('-'*20)
            print(self.group_name)
            print('max team factor problem: ' + \
                  str(self.team_factors))
            print('-'*20)

        if self.team_factors.min() < 0.8:
            print('min team factor problem: ' + \
                  str(self.team_factors))


    def get_self_ratings(self):
        self.self_factors = [student.self_factor for student in self.students]


    def latex_all(self, runlatex=0):
        for student in self.students:
            student.latex(runlatex=runlatex)


    def create_table(self):
        N = len(self.students)
        self.table = ['\\begin{tabular}{|l|'+'l|'*(N+1)+'}']
        out = self.table.append
        out('\\hline')
        out('Category & Team Ave. & ' + ' & '.join(self.firstnames) + ' \\\\')
        out('\\hline')
        fmt = ' %s ' + '& %0.2f '*(N+1) + '\\\\'
        team_ave = self.team_cat_ave_scores

        for n, area in enumerate(self.students[0].areas):
            if n % 2:
                out('\\rowcolor[gray]{0.9}')
            mytup = (area, team_ave[n]) + tuple(self.ave_scores[n,:])
            row_str = fmt % mytup
            out('\\rule{0pt}{1.1EM} ' + row_str)
            out('\\hline')
        mytup = ('Raw Ratios', self.raw_team_factors.mean()) + \
                         tuple(self.raw_team_factors)
        row_str = fmt % mytup
        out(row_str)
        out('\\hline')
        mytup = ('Ratios', self.team_factors.mean()) + \
                         tuple(self.team_factors)
        row_str = fmt % mytup
        out(row_str)
        out('\\hline')
        out('\\end{tabular}')
        return self.table


    def build_out_path(self):
        outname = self.group_name.replace(' ','_') + '_team_evals.tex'
        pathout = os.path.join(outfolder, outname)
        self.tex_path = pathout
        return pathout


    def latex_summary(self, runlatex=0):
        pathout = self.build_out_path()
        self.latex = ['\\input{../../header}']
        out = self.latex.append
        out(r'\pagestyle{fancy}')
        out(r'\lfoot{First Team Member Rating, After Written Proposals}')
        out(r'\cfoot{}')
        out(r'\rfoot{}')
        out(r'\renewcommand{\headrulewidth}{0pt}')
        out('\\begin{document}')
        out(r'\newcommand*{\mytitle}[1]{\begin{center}\textbf{#1}\end{center}}')
        out(r'\mytitle{\Large %s}' % self.group_name)
        out('')
        out('\\flushleft')
        out('\\textbf{Team Members: }' + self.name_str +' \\\\')
        out('')
        out('\\vspace{0.25in}')
        #out('\\input{../../ratings_body}')
        out('\\mysec{Ratings}')
        table_list = self.create_table()
        self.latex.extend(table_list)
        out('')
        out('\\end{document}')
        txt_mixin.dump(pathout, self.latex)
        if runlatex:
            pytexutils.RunLatex(pathout)


    def send_emails(self):
        for student in self.students:
            student.send_email()




class group_with_rst(group, section):
    def __init__(self, pathin, group_list=None, email_list=None, \
                 class_dict=None, subre='^-+$', alts={}, 
                 subclass=section_level_1):
        self.pathin = pathin
        self.group_list = group_list
        self.email_list = email_list
        self.class_dict = class_dict
        self.alts = alts
        raw_list = txt_mixin.read(pathin)
        #self.list = raw_list
        section.__init__(self, raw_list, subre=subre, \
                         subclass=subclass, has_title=0)
        self.get_group_name_from_path()
        if (group_list is not None) and (email_list is not None):
            self.find_members()
        
    def get_group_name_from_path(self):
        folder, filename = os.path.split(self.pathin)
        fno, ext = os.path.splitext(filename)
        self.group_name = fno.replace('_',' ')
        return self.group_name
    

    def break_into_sections(self, verbosity=1):
        ## if self.class_dict is None:
        ##     if verbosity > 0:
        ##         print('skipping break_into_sections because self.class_dict is None')
        ##     return
        inds = self.content.findallre(self.subre)
        if len(inds) == 0:
            return
        inds2 = [item-1 for item in inds]
        inds2.append(None)
        self.raw_sec_list = None
        prevind = inds2.pop(0)
        self.header = self.content[0:prevind]
        for ind in inds2:
            curlist = self.content[prevind:ind]
            if self.raw_sec_list is None:
                self.raw_sec_list = [curlist]
            else:
                self.raw_sec_list.append(curlist)
            prevind = ind
        self.sec_list = None

        for curlist in self.raw_sec_list:
            curtitle = curlist[0]
            if self.class_dict is None:
                curclass = default_section_no_children
            else:
                curclass = self.class_dict[curtitle]
            cur_sec = curclass(curlist)
            cur_sec.calc_grade()
            if self.sec_list is None:
                self.sec_list = [cur_sec]
            else:
                self.sec_list.append(cur_sec)

##     def break_into_sections(self, pat='^-+$'):
##         inds = self.findallre(pat)
##         inds2 = [item-1 for item in inds]
##         inds2.append(None)
##         self.raw_sec_list = None
##         prevind = inds2.pop(0)
##         self.header = self.list[0:prevind]
##         for ind in inds2:
##
##                curlist = self.list[prevind:ind]
##             if self.raw_sec_list is None:
##                 self.raw_sec_list = [curlist]
##             else:
##                 self.raw_sec_list.append(curlist)
##             prevind = ind
##         self.sec_list = None

##         for curlist in self.raw_sec_list:
##             cur_sec = section(curlist)
##             if self.sec_list is None:
##                 self.sec_list = [cur_sec]
##             else:
##                 self.sec_list.append(cur_sec)


    def get_time_lines(self):
        time_titles = ['Timing','Time']
        for n, section in enumerate(self.sec_list):
            q = timing_pat.search(section.title)
            if q:
                self.time_ind = n + 1#plus one because group name will
                #be in the first column
                return section.content
            
    ## def get_time_lines(self):
    ##     for n, section in enumerate(self.sec_list):
    ##         if section.title == 'Timing':
    ##             self.time_ind = n + 1#plus one because group name will
    ##                                  #be in the first column
    ##             return section.content

        
    def get_speaking_lines(self):
        for n, section in enumerate(self.sec_list):
            if section.title == 'Speaking and Delivery':
                self.speaking_ind = n + 1#plus one because group name will
                                     #be in the first column
                return section.content


    def build_speaking_rst(self, runlatex=1):
        self.speaking_lines = txt_mixin.txt_list(self.get_speaking_lines())
        dec_inds = self.speaking_lines.findallre('^\++$')
        start_inds = [item-1 for item in dec_inds]
        speaker_list = None
        start_inds.append(None)
        prev_ind = start_inds.pop(0)
        for ind in start_inds:
            curlines = self.speaking_lines[prev_ind:ind]
            curspeaker = speaker(curlines, self)
            curspeaker.build_rst()
            curspeaker.save_rst()
            if runlatex:
                curspeaker.run_rst()
            if speaker_list is None:
                speaker_list = [curspeaker]
            else:
                speaker_list.append(curspeaker)
            prev_ind = ind
        self.speaker_list = speaker_list
        
    

    def find_time_string(self, linesin):
        pat = re.compile('(\\d+:\\d+)')
        for line in linesin:
            q = pat.search(line)
            if q:
                return q.group(1)

    def parse_time_string(self, stringin):
        min_str, sec_str = stringin.split(':',1)
        time = float(min_str) + float(sec_str)/60.0
        self.time = time
        return self.time

    def get_timing_grade(self):
        time_lines = self.get_time_lines()
        time_str = self.find_time_string(time_lines)
        time = self.parse_time_string(time_str)
        if time > 9.2:
            num_steps = int((time-9.0)/0.5)
            penalty = -0.1*num_steps
        else:
            penalty = 0.0
        self.time_penalty = penalty
    

    def get_section_labels(self):
        labels = ['Group Name']
        for section in self.sec_list:
            labels.extend(section.get_labels())
        self.labels = labels
        self.labels.append('Overall Score')
        return self.labels


    def calc_overall_score(self):
        grades = None
        appearance = 0.0
        timing = 0.0
        for section in self.sec_list:
            if hasattr(section,'grade'):
                elem = float(section.grade)
                if grades is None:
                    grades = [elem]
                else:
                    grades.append(elem)
        self.ave = mean(grades)
        if hasattr(self, 'time_penalty'):
            self.ave += self.time_penalty
        return self.ave


    def build_spreadsheet_row(self, look_for_penalty=False):
        row_out = [self.get_group_name_from_path()]
        for section in self.sec_list:
            row_out.extend(section.get_grades())
        #Pdb().set_trace()
        if look_for_penalty:
            if self.find_section('Penalty') is None:
                row_out.append(0.0)
        overall = self.calc_overall_score()
        row_out.append(overall)
        self.row_out = row_out
        return self.row_out


    def build_team_rst_output(self):
        self.team_rst = copy.copy(self.header)
        for cur_sec in self.sec_list:
            self.team_rst.append('')
            self.team_rst.append(cur_sec.title)
            self.team_rst.append(cur_sec.dec_line)
            if cur_sec.title == 'Speaking and Delivery':
                self.team_rst.append(':grade:`%s`' % cur_sec.grade)
            else:
                self.team_rst.extend(cur_sec.content)
            if cur_sec.title == 'Timing':
                self.team_rst.append('')
                self.team_rst.append('**Timing Penalty:** %0.4g' % \
                                     self.time_penalty)
            self.team_rst.append('')
        self.team_rst.append('')
        overall_title = mysecdec('Overall Grade')
        self.team_rst.extend(overall_title)
        self.team_rst.append(':grade:`%0.3g`' % self.overall_grade)


    def save_team_rst(self, outpath):
        self.outpath = outpath
        txt_mixin.dump(outpath, self.team_rst)

    def set_outpath(self, outpath):
        self.outpath = outpath

    def set_pdfpath(self):
        pne, ext = os.path.splitext(self.outpath)
        self.pdfpath = pne+'.pdf'
        
    def rst_team(self, clean=False):
        if clean:
            cmd = 'rst2latex_rwk.py -c 2 ' + self.outpath
        else:
            cmd = 'rst2latex_rwk.py ' + self.outpath
        os.system(cmd)
        self.set_pdfpath()


    def pdfpath_checker(self):
        if not hasattr(self,'pdfpath'):
            print('The group_with_rst instance does not have a pdfpath attribute.')
            return
        if not os.path.exists(self.pdfpath):
            print('pdf does not exist: '+self.pdfpath)
            return
        

    def compose_and_send_team_gmail(self, subject, debug=0):#, ga):
        """ga is a gmail account instance from libgmail that has
        already been logged into."""
        if not hasattr(self,'pdfpath'):
            print('you must call pres_rst_parser.rst_team before sending team email')
            return
        if not os.path.exists(self.pdfpath):
            print('pdf does not exist: '+self.pdfpath)
            return
        
        #emails = self.get_emails()
        if debug:
            emails = ['ryanlists@gmail.com']
        else:
            emails = self.emails

        #print('emails=' + str(emails))
        #addresses = emails.replace(';',',')
        #addresses = ['ryanwkrauss@gmail.com', 'ryanlists@gmail.com']

        body = "The attached pdf contains your team grade and my feedback."
        body += mysig

        gmail_smtp.sendMail(emails, subject, body, self.pdfpath)
        
##         msg = libgmail.GmailComposedMessage(addresses, subject, body, \
##                                             filenames=[self.pdfpath])


    def find_section(self, title):
        for sec in self.sec_list:
            if sec.title == title:
                return sec
            
        
class proposal(group_with_rst):
    def calc_overall_score(self):
        weight_dict = {#'Literature Review':0.05, \#lit. review is a
                       #separate grade
                       'Contemporary Issues':0.05, \
                       'Writing: Quick Read':0.20, \
                       'Writing: Slow Read':0.25, \
                       'Content':0.5}
        self.overall_grade = 0.0
        for key, weight in weight_dict.iteritems():
            cursec = self.find_section(key)
            self.overall_grade += weight*cursec.grade*10.0
        ec = self.find_section('Extra Credit')
        if ec is not None:
            print('before ec, overall_grade='+str(self.overall_grade))
            self.overall_grade += ec.grade
            print('after ec, overall_grade='+str(self.overall_grade))
        self.penalty = self.find_section('Penalty')
        if self.penalty is not None:
            multiplier = (1.0 + self.penalty.grade/100.0)
            print('before penalty, overall_grade='+str(self.overall_grade))
            self.overall_grade *= multiplier
            print('after penalty, overall_grade='+str(self.overall_grade))
            
        return self.overall_grade


    def build_team_rst_output(self):
        """Note that all grades must be calculated before calling this
        method."""
        self.team_rst = copy.copy(self.header)
        for cur_sec in self.sec_list:
            self.team_rst.append('')
            self.team_rst.extend(cur_sec.create_rst())
            self.team_rst.append('')
        self.team_rst.append('')
        overall_title = mysecdec('Overall Grade')
        self.team_rst.extend(overall_title)
        formula_line = '10*(0.5*(Contemporary Issues) + ' + \
                       '0.2*(Quick Read Weighted Average) + ' + \
                       '0.25*(Slow Read Weighted Average) + ' + \
                       '0.5*(Content Weighted Average))'
        if self.penalty is not None:
            formula_line += '* (1 + penalty/100)'
        self.team_rst.append('**Formula:**')
        self.team_rst.append('')
        self.team_rst.append('.. raw:: latex')
        self.team_rst.append('')
        ws = ' '*4
        out = self.team_rst.append
        def eq_out(strin):
            out(ws + strin)
        eq_out('\\newcommand{\\myrule}{\\rule{0pt}{1EM}}')
        eq_out(r'\begin{equation*}\begin{split}')
        eq_out(r'\textrm{grade} = & 10 \left( \myrule 0.05(\textrm{Contemporary Issues}) \right. \\')
        eq_out(r'& + 0.15 (\textrm{Quick Read Weighted Average}) ')
        eq_out(r'+ 0.25 (\textrm{Slow Read Weighted Average}) \\')
        eq_out(r'& \left. + 0.5 (\textrm{Content Weighted Average}) \myrule \right)')
        if self.penalty is not None:
            eq_out(r'\times (1 + \textrm{Penalty}/100)')
        eq_out(r'\end{split}\end{equation*}')
        self.team_rst.append('')
        self.team_rst.append('')
        self.team_rst.append(':grade:`%0.1f`' % self.overall_grade)



    def compose_and_send_team_gmail(self):#, subject):#, ga):
        self.pdfpath_checker()
        subject = "ME 482: Proposal Grade"
        body = "The attached pdf contains your team proposal grade and my feedback."

        gmail_smtp.sendMail(self.emails, subject, body, self.pdfpath)



class presentation_with_appearance(group_with_rst):
#    Appearance
#    Content and Organization
#    Speaking and Delivery
#    Slides
#    Listening to and Answering Questions
 
    def __init__(self, *args, **kwargs):
        group_with_rst.__init__(self, *args, **kwargs)
        if kwargs.has_key('weight_dict'):
            weight_dict = kwargs['weight_dict']
        else:
            weight_dict = {'Appearance':0.05,\
                           'Content and Organization':0.5, \
                           'Speaking and Delivery':0.25, \
                           'Slides':0.15,\
                           'Listening to and Answering Questions':0.05}
        self.weight_dict = weight_dict
        self.get_timing_grade()


    
    def calc_overall_score(self):
        self.overall_grade = 0.0
        for key, weight in self.weight_dict.iteritems():
            cursec = self.find_section(key)
            self.overall_grade += weight*cursec.grade
        ec = self.find_section('Extra Credit')
        if ec is not None:
            print('before ec, overall_grade='+str(self.overall_grade))
            self.overall_grade += ec.grade
            print('after ec, overall_grade='+str(self.overall_grade))
        self.penalty = self.find_section('Penalty')
        if self.penalty is not None:
            multiplier = (1.0 + self.penalty.grade/100.0)
            print('before penalty, overall_grade='+str(self.overall_grade))
            self.overall_grade *= multiplier
            print('after penalty, overall_grade='+str(self.overall_grade))

        return self.overall_grade


    def build_spreadsheet_row(self):
        row_out = [self.get_group_name_from_path()]
        for section in self.sec_list:
            if hasattr(section,'grade'):
                elem = str(section.grade)
            else:
                elem = ';'.join(section.content)#this is how we handle timing and notes

            row_out.append(elem)
        ## if self.find_section('Penalty') is None:
        ##     row_out.append(0.0)
        overall = self.calc_overall_score()
        row_out.append(overall)
        row_out.insert(self.time_ind+1, self.time_penalty)
        self.row_out = row_out
        return self.row_out


    def get_section_labels(self):
        group_with_rst.get_section_labels(self)
        self.labels.insert(self.time_ind+1, 'Time Penalty')
        return self.labels


    def get_timing_grade(self):
        time_lines = self.get_time_lines()
        time_str = self.find_time_string(time_lines)
        time = self.parse_time_string(time_str)
        if time > 15.0:
            num_steps = int((time-9.0)/0.5)
            penalty = -0.1*num_steps
        else:
            penalty = 0.0
        self.time_penalty = penalty


class update_presentation(presentation_with_appearance):
#    Appearance
#    Content and Organization
#    Speaking and Delivery
#    Slides
#    Listening to and Answering Questions

    def __init__(self, *args, **kwargs):
        group_with_rst.__init__(self, *args, **kwargs)
        if kwargs.has_key('weight_dict'):
            weight_dict = kwargs['weight_dict']
        else:
            weight_dict = {'Content and Organization':0.5, \
                           'Speaking and Delivery':0.3, \
                           'Slides':0.1,\
                           'Listening to and Answering Questions':0.1}
        self.weight_dict = weight_dict
        self.get_timing_grade()



    def calc_overall_score(self):
        presentation_with_appearance.calc_overall_score(self)
        self.overall_grade += self.time_penalty
        return self.overall_grade


    def get_timing_grade(self):
        time_lines = self.get_time_lines()
        #Pdb().set_trace()
        time_str = self.find_time_string(time_lines)
        time = self.parse_time_string(time_str)
        penalty = 0.0
        if time > 7.45:
            num_steps = int((time-7.0)/0.5)
            penalty = -0.15*num_steps
        elif time < 4.55:
            num_steps = int((5.0-time)/0.5)
            penalty = -0.15*num_steps
        self.time_penalty = penalty


class update_presentation_no_timing_penalty(update_presentation):
    def __init__(self, *args, **kwargs):
        group_with_rst.__init__(self, *args, **kwargs)
        if kwargs.has_key('weight_dict'):
            weight_dict = kwargs['weight_dict']
        else:
            weight_dict = {'Content and Organization':0.55, \
                           'Speaking and Delivery':0.35, \
                           'Slides':0.1,\
                           'Listening to and Answering Questions':0.0}
        self.weight_dict = weight_dict
        self.get_timing_grade()

    def get_timing_grade(self):
        time_lines = self.get_time_lines()
        #Pdb().set_trace()
        time_str = self.find_time_string(time_lines)
        time = self.parse_time_string(time_str)
        penalty = 0.0
        ## if time > 7.45:
        ##     num_steps = int((time-7.0)/0.5)
        ##     penalty = -0.15*num_steps
        ## elif time < 4.55:
        ##     num_steps = int((5.0-time)/0.5)
        ##     penalty = -0.15*num_steps
        self.time_penalty = penalty
    
