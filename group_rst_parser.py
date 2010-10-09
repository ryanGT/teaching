"""This is a second attempt at a module for compiling and emailing
group grades from feedback typed into an rst form.  This module will
generalize presentation_rst_parser.py so that the classes can be used
for emailing and compiling grades on the written proposals."""

import txt_mixin, spreadsheet, rst_creator, rwkos
import re, os
import gmail_smtp
reload(gmail_smtp)

from scipy import mean

from IPython.Debugger import Pdb

grade_pat = re.compile(':grade:`(.*)`')

import copy
reload(spreadsheet)

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

class contemp_issues(lit_review):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.05

class extra_credit(lit_review):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1
    
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
                           'Organization and Flow': 0.8, \
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
        self.outpath = pne + '_' + self.name + ext
        
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
        
    def send_email(self, subject):
        email = self.email
        #addresses = ['ryanwkrauss@gmail.com', 'ryanlists@gmail.com', 'ryanwkrauss@att.net']
        body = "The attached pdf contains feedback on your individual speaking and delivery grade."
        gmail_smtp.sendMail(email, subject, body, self.pdfpath)


class group_with_rst(section):
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
        if self.class_dict is None:
            if verbosity > 0:
                print('skipping break_into_sections because self.class_dict is None')
            return
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
##             curlist = self.list[prevind:ind]
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
        for n, section in enumerate(self.sec_list):
            if section.title == 'Timing':
                self.time_ind = n + 1#plus one because group name will
                                     #be in the first column
                return section.content

        
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


    def build_spreadsheet_row(self):
        row_out = [self.get_group_name_from_path()]
        for section in self.sec_list:
            row_out.extend(section.get_grades())
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
                self.team_rst.append('**Timing Penalty: %0.4g**' % \
                                     self.time_penalty)
            self.team_rst.append('')
        self.team_rst.append('')
        overall_title = mysecdec('Overall Grade')
        self.team_rst.extend(overall_title)
        self.team_rst.append(':grade:`%0.3g`' % self.ave)


    def save_team_rst(self, outpath):
        self.outpath = outpath
        txt_mixin.dump(outpath, self.team_rst)

    def set_outpath(self, outpath):
        self.outpath = outpath

    def set_pdfpath(self):
        pne, ext = os.path.splitext(self.outpath)
        self.pdfpath = pne+'.pdf'
        
    def rst_team(self):
        cmd = 'rst2latex_rwk.py -c 2 ' + self.outpath
        os.system(cmd)
        self.set_pdfpath()

    def find_members(self):
        lastnames, firstnames = self.group_list.get_names(self.group_name)
        self.lastnames = lastnames
        self.firstnames = firstnames
        for n, lastname in enumerate(lastnames):
            if self.alts.has_key(lastname):
                self.firstnames[n] = self.alts[lastname]
        members = None
        for last, first in zip(self.lastnames, self.firstnames):
            email = self.email_list.get_email(last)
            curmember = member(last, first, email)
            if members is None:
                members = {first:curmember}
            else:
                members[first] = curmember
        self.members = members
        self.emails = self.email_list.get_emails(lastnames)
        return self.emails


    def pdfpath_checker(self):
        if not hasattr(self,'pdfpath'):
            print('The group_with_rst instance does not have a pdfpath attribute.')
            return
        if not os.path.exists(self.pdfpath):
            print('pdf does not exist: '+self.pdfpath)
            return
        

    def compose_and_send_team_gmail(self, subject):#, ga):
        """ga is a gmail account instance from libgmail that has
        already been logged into."""
        if not hasattr(self,'pdfpath'):
            print('you must call pres_rst_parser.rst_team before sending team email')
            return
        if not os.path.exists(self.pdfpath):
            print('pdf does not exist: '+self.pdfpath)
            return
        
        #emails = self.get_emails()
        emails = self.emails
        #print('emails=' + str(emails))
        #addresses = emails.replace(';',',')
        #addresses = ['ryanwkrauss@gmail.com', 'ryanlists@gmail.com']

        body = "The attached pdf contains your team grade and my feedback."

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
        eq_out(r'\end{split}\end{equation*}')
        self.team_rst.append('')
        self.team_rst.append('')
        self.team_rst.append(':grade:`%0.3g`' % self.overall_grade)



    def compose_and_send_team_gmail(self):#, subject):#, ga):
        self.pdfpath_checker()
        subject = "ME 482: Proposal Grade"
        body = "The attached pdf contains your team proposal grade and my feedback."

        gmail_smtp.sendMail(self.emails, subject, body, self.pdfpath)

