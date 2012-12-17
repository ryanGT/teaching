"""This is a second attempt at a module for compiling and emailing
group grades from feedback typed into an rst form.  This module will
generalize presentation_rst_parser.py so that the classes can be used
for emailing and compiling grades on the written proposals."""

import txt_mixin, spreadsheet, rst_creator, rwkos
import re, os
import gmail_smtp
reload(gmail_smtp)
from numpy import array, where, zeros

from scipy import mean

from IPython.core.debugger import Pdb

grade_pat = re.compile(':grade:`(.*)`')
timing_pat = re.compile('^Tim(ing|e)[: ]*$')
notes_pat = re.compile('^Notes*[: ]*$')

import copy
reload(spreadsheet)

mysig = """

--
Ryan Krauss, Ph.D.
Associate Professor
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
                 has_title=True, max_grade=10.0, verbosity=1):
        #print('raw_list=')
        #print('\n'.join(raw_list))
        self.max_grade = max_grade#used for checking grade corrections
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
                try:
                    cur_grade = float(q.group(1))
                except ValueError:
                    if verbosity > 0:
                        print('warning, found empty grade')
                    cur_grade = 0.0
                if grades is None:
                    grades = [cur_grade]
                else:
                    grades.append(cur_grade)
            self.grade = mean(grades)

        self.subre = subre
        self.subclass = subclass
        if (subre is not None) and (subclass is not None):
            self.break_into_sections()


    def get_grade_from_line(self, line):
        q = grade_pat.search(line)
        cur_grade = float(q.group(1))
        return cur_grade


    def get_grade_from_ind(self, ind):
        grade_line = self.content[ind]
        return self.get_grade_from_line(grade_line)


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
                if sec is None:
                    print('did not find a section with the title ' + title)
                else:
                    self.total_weight += weight
                    self.weighted_total += sec.grade * weight
            self.grade = self.weighted_total/self.total_weight


    def correct_grade(self, correction_factor, fmt='%0.2g'):
        #self.grade = newgrade
        inds = self.content.findall(':grade:`')
        N = len(inds)
        expected_grades = 1
        msg = "Problem with finding exactly one grade to replace, N = " + str(N)
        if self.title == 'Speaking and Delivery':
            expected_grades = len(self.sec_list)
            msg = "Grades to replace does not equal number of speakers, N = " + str(N)
        assert N == expected_grades, msg
        grade_fmt = ':grade:`' + fmt + '`'
        for ind in inds:
            old_grade = self.get_grade_from_ind(ind)
            new_grade = old_grade*correction_factor
            if new_grade > self.max_grade:
                new_grade = self.max_grade
            new_grade_line = grade_fmt % new_grade
            self.content[ind] = new_grade_line


    def __repr__(self):
        outstr = ""
        if self.title is not None:
            outstr += self.title+'\n'
        if self.dec_line is not None:
                 outstr += self.dec_line +'\n'
        content_str = '\n'.join(self.content)
        outstr += content_str
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
    ## def __init__(self, *args, **kwargs):
    ##     section_level_1.__init__(self, *args, **kwargs)
    ##     self.weight = 0.15
    ##     self.subweights = {'Abstract':1.0, \
    ##                        'Introduction':1.0, \
    ##                        'Conclusion':1.0, \
    ##                        'Organization':0.2}

    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1
        self.subweights = {'Abstract':1.0, \
                           'Introduction':1.0, \
                           'Conclusion':1.0, \
                           }


    def create_rst(self):
        section_level_1.create_rst(self)
        self.rst.append('')
        sublist = subsec_dec('Weighted Average: '+self.title)
        self.rst.extend(sublist)
        self.rst.append(':grade:`%0.3g`' % self.grade)
        return self.rst


class slow_read(quick_read):
    ## def __init__(self, *args, **kwargs):
    ##     section_level_1.__init__(self, *args, **kwargs)
    ##     self.weight = 0.25
    ##     self.subweights = {'Problem Statement and Formulation': 1.0, \
    ##                        'Organization and Flow': 0.5, \
    ##                        'Clarity and Tone': 1.0, \
    ##                        'Format/Style': 1.0, \
    ##                        'Required Sections': 0.2, \
    ##                        'Technical Language': 1.0, \
    ##                        'Grammar and Spelling': 1.0}

    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.15
        self.subweights = {'Organization and Flow': 1.0, \
                           'Clarity and Tone': 1.0, \
                           'Format/Style': 1.0, \
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





class intro_and_problem_statement(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.2
        self.subweights = {'Problem Statement and Formulation': 1.0, \
                           'Design Goals': 1.0, \
                           'Testing Plans': 1.0, \
                           'Constraints': 1.0, \
                           }

class intro_and_problem_statement_final_report(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1
        self.subweights = {'Problem Statement and Formulation': 1.0, \
                           'Design Goals': 1.0, \
                           'Constraints': 1.0, \
                           }

class intro_and_bg_reading_mini_project(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1
        self.subweights = {'Background Reading': 1.0, \
                           'Definition of Engineering Design': 1.0, \
                           'Convergent and Divergent Thinking': 1.0, \
                           'The Role of Analysis': 1.0, \
                           'What Did You Learn?': 1.0, \
                           }

class design_methodology_mini_project(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.15
        self.subweights = {'Discussion': 1.0, \
                           'Validity of the Approach': 1.0, \
                           }


class analysis_mini_project(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.2
        self.subweights = {'Thoroughness and Approach': 1.0, \
                           'Explanation': 1.0, \
                           'Connection to Decisions': 1.0, \
                           }


class final_design_mini_project(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1
        self.subweights = {'Explanation': 1.0, \
                           }


class budget_mini_project(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1
        self.subweights = {'Explanation': 1.0, \
                           }

class performance_mini_project(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.05
        self.subweights = {'Explanation': 1.0, \
                           'Expectations': 0.5, \
                           }

class conclussions_mini_project(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.05
        self.subweights = {'Effectiveness': 1.0, \
                           }



class lit_review_and_br(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.05
        self.subweights = {'Literature Review': 1.0, \
                           'Background Research': 0.5, \
                           }

class design_strategy(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.2
        self.subweights = {'Design Strategy': 1.0, \
                           'Preliminary Design Ideas': 1.0, \
                           'Discussion of Risks': 1.0, \
                           'Backup Plans': 1.0, \
                           'Design Methodology': 1.0, \
                           }


class analysis(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.2
        self.subweights = {'Analysis Plans': 1.0, \
                           'Preliminary Analysis': 1.0, \
                           'Feasibility Calculations': 1.0, \
                           'Connection to Decisions': 0.7, \
                           }

class design(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.25
        self.subweights = {'Design Methodology':1.0, \
                           'Completeness':1.0, \
                           'Quality of the Design':1.0, \
                           'Explanation':1.0, \
                           'Risks and Back-up Plans':1.0, \
                           }


class design_final_report(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.2
        self.subweights = {'Design Methodology':1.0, \
                           'Quality of the Design':1.0, \
                           'Explanation':1.0, \
                           'Strengths and Weaknesses':1.0, \
                           }


class analysis_design_review(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.25
        self.subweights = {'Preliminary Analysis and Feasibility Calculations':1.0, \
                           'Analysis Completed':1.0, \
                           'Explanation':1.0, \
                           'Connection to Decisions':1.0, \
                           'Thoroughness and Approach':1.0, \
                           }


class analysis_final_report(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.25
        self.subweights = {'Thoroughness and Approach':1.0, \
                           'Explanation':1.0, \
                           'Connection to Decisions':1.0, \
                           }


class prototype_construction(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1
        self.subweights = {'Discussion':1.0, \
                           'Challenges':1.0, \
                           'Modifications':1.0, \
                           }



class testing(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.1
        self.subweights = {'Coverage and Appropriateness':1.0, \
                           'Methodology':1.0, \
                           'Presentation of Results':1.0, \
                           }




class miscellaneous(quick_read):
    def __init__(self, *args, **kwargs):
        section_level_1.__init__(self, *args, **kwargs)
        self.weight = 0.05
        self.subweights = {'Timeline': 1.0, \
                           'Budget': 1.0, \
                           'Computers and Software': 1.0, \
                           }


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
        if self.name.find(' ') > -1:
            first, last = self.name.split(' ',1)
            me = self.parent.find_member(first, last)
        else:
            me = self.parent.find_member(self.name)
        ## try:
        ##     me = self.parent.find_member(first, last)
        ## except:
        ##     bad = False
        ##     if self.name.find(' ') > -1:
        ##         try:
        ##             first, last = self.name.split(' ',1)
        ##             me = self.parent.members[first]
        ##         except ValueError:
        ##             bad = True
        ##     else:
        ##         bad = True
        ##     if bad:
        ##         print('could not find self.name in parent.firstnames')
        ##         print('    self.name=' + str(self.name))
        ##         print('    parent.firstnames=' + str(self.parent.firstnames))
        ##         print('    parent.lastnames=' + str(self.parent.lastnames))
        ##         return
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
        self.rst.append('')
        self.rst.append('.. sectnum::')
        self.rst.append('    :depth: 0')
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


def find_min_last_initials(last, other_lasts):
    N = len(last)

    for i in range(1,N):
        test = last[0:i]
        found = 0
        for olast in other_lasts:
            if olast.find(test) > -1:
                found = 1
                break
        if not found:
            return test


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
        self.append_initials_to_alt_firsts()
        members = None
        emails = []

        for last, first, last_initials in \
                zip(self.lastnames, self.alt_firstnames, self.last_initials):
            try:
                email = self.email_list.get_email(last)
            except AssertionError:
                email = self.email_list.get_email(last, first)
            emails.append(email)
            curmember = member(last, first, email)
            key = first
            if last_initials:
                key += ' ' + last_initials + '.'
            if members is None:
                members = {key:curmember}
            else:
                members[key] = curmember
        self.members = members
        self.N = len(self.members)
        self.emails = emails#self.email_list.get_emails(lastnames)
        return self.emails


    def append_initials_to_firstnames(self):
        """Fix self.firstnames by appending a last initial if
        necessary."""
        self.firstnames = txt_mixin.txt_list(self.firstnames)
        self.raw_firstnames = copy.copy(self.firstnames)
        N = len(self.firstnames)
        self.last_initials = ['']*N
        for i in range(N):
            first = self.firstnames[i]
            inds = self.firstnames.findall(first)
            if len(inds) > 1:
                matching_last = [self.lastnames[ind] for ind in inds]
                for j in inds:
                    first = self.firstnames[j]
                    last = self.lastnames[j]
                    other_lasts = [olast for olast in matching_last \
                                   if (olast != last)]
                    last_initials = find_min_last_initials(last, other_lasts)
                    self.last_initials[j] = last_initials
                    first += ' ' + last_initials + '.'
                    self.firstnames[j] = first


    def append_initials_to_alt_firsts(self):
        """For the name for of the latex team member rating sheets, I
        need Dan St. and Dan Sp.  These are alt first plus initials."""
        if not hasattr(self, 'last_initials'):
            self.append_initials_to_firstnames()
            
        alts_with_initials = []
        for alt, initials in zip(self.alt_firstnames, self.last_initials):
            out = alt
            if initials:
                out += ' ' + initials + '.'
            alts_with_initials.append(out)
        self.alts_with_initials = alts_with_initials
        return self.alts_with_initials


    def get_firstname_no_initials(self, first, last=None):
        """I am still trying to kill all bugs stemminf from Daniel
        Sprehe and Daniel Strackeljahn being on the same team.
        self.names now has keys like (Daniel Sp., Sprehe) and I need
        Dan_Sprehe.tex for my filename.  How do I get from Daniel
        Sp. back to Dan?  My approach is to drop the middle initials
        and just return that unless last is not None and is in the
        self.alts dictionary."""
        if first.find(' ') > -1:
            first, middle = first.split(' ',1)
        if last is not None:
            if self.alts.has_key(last):
                first = self.alts[last]
        return first
    

    def find_member(self, first, last=None):
        """This method seeks to find the correct student corresponding
        to the first and last name.  This should be easy if there is
        only one student with a given first name.  It gets tricky if
        there are multiple students with the same name and especially
        the same last initial."""
        mykeys = txt_mixin.txt_list(self.members.keys())
        inds = mykeys.findall(first)
        if len(inds) == 1:
            #we found exactly one student with a matching firstname
            ind = inds[0]
            key = mykeys[ind]
            return self.members[key]
        elif len(inds) == 0:
            raise ValueError, '%s not found in self.members.keys(): %s' % \
                  (first, self.members.keys())
        elif len(inds) > 1:
            assert last, "Found more than one first name match, but last name not specified."
            #we have more than one match for first
            #keep adding last initials until there is only one match
            matching_keys = [mykeys[ind] for ind in inds]
            match_with_intials = []
            for key in matching_keys:
                first, last_init = key.split(' ',1)
                if last_init[-1] == '.':
                    last_init = last_init[0:-1]#drop trailing period
                if last.find(last_init) == 0:
                    match_with_intials.append(key)
            assert len(match_with_intials) > 0, \
                   "Did not find a last initials match"
            assert len(match_with_intials) == 1, \
                   "Found more than one last initials match"
            return self.members[match_with_intials[0]]
        

    def compose_and_send_team_gmail(self, subject, body, debug=0, \
                                    attach_sig=True):
        if debug:
            emails = ['ryanlists@gmail.com']
        else:
            emails = self.emails
            
        if attach_sig:
            body += '\n' + mysig

        gmail_smtp.send_mail_siue(emails, subject, body)


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
        self.copy_team_factors_to_raw()
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

        N = len(self.members)

        self.team_factor_ave_vect = array([self.team_factor_ave]*N)
        assert self.team_factor_ave > 0.92, "Team with really low average: %s: %0.4g" % (self.group_name, self.team_factor_ave)
        assert self.team_factor_ave < 1.03, "Team with really high average: %s: %0.4g" % (self.group_name, self.team_factor_ave)

        for student, tf in zip(self.students, self.team_factors):
            student.team_factor = tf


    def build_name_str(self):
        N = len(self.members)
        if not hasattr(self, 'names'):
            self.build_names_tuples()
        if N == 1:
            self.name_str = ' '.join(self.names[0])
        else:
            name_str = ''
            for n, pair in enumerate(self.names):
                if n > 0:
                    name_str +=', '
                if n == (N-1):
                    name_str += 'and '
                firstname = pair[0]
                lastname = pair[1]
                clean_first = self.get_firstname_no_initials(firstname,lastname)
                name_str +=  clean_first + ' ' + lastname
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


    def build_out_path(self, outfolder=''):
        outname = self.group_name.replace(' ','_') + '_team_evals.tex'
        pathout = os.path.join(outfolder, outname)
        self.tex_path = pathout
        return pathout


    def latex_summary(self, runlatex=0, outfolder=''):
        pathout = self.build_out_path(outfolder=outfolder)
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


class grade_subsection(object):
    def __init__(self, title, optional):
        self.title = title
        self.optional = optional


class grade_major_section(object):
    """A major section that has optional subsections, subsection_dict
    is a dictionary of subsection_titles:optional (bool)"""
    def __init__(self, title, sublist, optlist):
        self.title = title
        self.subsections = []
        for subtitle in sublist:
            opt = False
            if subtitle in optlist:
                opt = True
            cursub = grade_subsection(subtitle, opt)
            self.subsections.append(cursub)


    def get_labels(self):
        mylist = [sub.title for sub in self.subsections]
        mylist.append(self.title)
        return mylist
        


class grade_major_section_no_subs(grade_major_section):
    """A major section such as Contemporary Issues that has no
    subsections."""
    def __init__(self, title):
        self.title = title
        self.subsections = []


class grade_major_section_all_subs_required(grade_major_section):
    """class for a major section where all the subsections are
    required.  subsection_titles is simply a list of the titles of the
    subsections."""
    def __init__(self, title, subsection_titles):
        self.title = title
        self.subsections = []
        for title in subsection_titles:
            cursub = grade_subsection(title, False)
            self.subsections.append(cursub)


class proposal_grade_map_2011(object):
    """Some students omitted certain subsections in their proposals
    that they felt were redundant or unnecessary.  This is OK for
    certain subsections, but it makes a mess of my spreadsheet.  This
    class tries to map student grades to a spreadsheet row while
    allowing certain subsections to be missing.  It depends on the
    classes above:

    grade_subsection, grade_major_section,
    grade_major_section_no_subs, and
    grade_major_section_all_subs_required"""
    def get_labels(self):
        mylist = []

        for section in self.major_sections:
            curlist = section.get_labels()
            mylist.extend(curlist)

        return mylist

    
    def append_required(self, titles, lists):
        for curtitle, curlist in zip(titles, lists):
            cursec = grade_major_section_all_subs_required(curtitle, \
                                                           curlist)
            self.major_sections.append(cursec)


    def append_no_sub(self, title):
        cursub = grade_major_section_no_subs(title)
        self.major_sections.append(cursub)


    def append_optional(self, title, sublist, optlist):
        cursec = grade_major_section(title,sublist, optlist)
        self.major_sections.append(cursec)


    def _append_quick_read(self):
        title1 = 'Writing: Quick Read'
        list1 = ['Abstract', \
                 'Introduction', \
                 'Conclusion', \
                 ]

        self.append_required([title1], [list1])


    def _append_introduction_and_prob_statement(self):
        title2 = 'Introduction and Problem Statement'
        list2 = ['Problem Statement and Formulation', \
                 'Design Goals', \
                 'Testing Plans', \
                 'Constraints']

        self.append_required([title2], [list2])


    def _append_lit_review_and_back_res(self):
        title3 = 'Literature Review and Background Research'
        list3 = ['Literature Review','Background Research']

        self.append_required([title3], [list3])



    def _append_analysis(self):
        title6 = 'Analysis'
        list6 = ['Analysis Plans', \
                 'Preliminary Analysis', \
                 'Feasibility Calculations', \
                 'Connection to Decisions']
        opt_list6 = ['Preliminary Analysis', 'Connection to Decisions', \
                     'Feasibility Calculations']

        self.append_optional(title6, list6, opt_list6)


    def _append_misc(self):
        title7 = 'Miscellaneous'
        list7 = ['Timeline','Budget','Computers and Software']

        self.append_required([title7], [list7])


    def _append_slow_read(self):
        title8 = 'Writing: Slow Read'
        list8 = ['Organization and Flow', 'Clarity and Tone', \
                 'Format/Style','Technical Language', \
                 'Grammar and Spelling']

        self.append_required([title8], [list8])


    def _append_design_strategy(self):
        title5 = 'Design Strategy'
        list5 = ['Design Strategy', 'Preliminary Design Ideas', \
                 'Discussion of Risks', 'Backup Plans', \
                 'Design Methodology']
        opt_list5 = ['Design Strategy', 'Backup Plans']

        self.append_optional(title5, list5, opt_list5)



    def __init__(self):

        self.major_sections = []#you must do this before calling the _append* methods

        self._append_quick_read()
        self._append_introduction_and_prob_statement()
        self._append_lit_review_and_back_res()

        title4 = 'Contemporary Issues'
        self.append_no_sub(title4)

        self._append_design_strategy()
        self._append_analysis()
        self._append_misc()
        self._append_slow_read()



    def build_row(self, group_with_rst, missing_val=''):
        """Intelligently pull grades out of a group_with_rst instance,
        allowing some to be missing."""
        row_out = []
        total_missing = 0
        for section in self.major_sections:
            group_sec = group_with_rst.find_section(section.title)
            for subsection in section.subsections:
                subsec = group_sec.find_section(subsection.title)
                if subsec is not None:
                    row_out.append(subsec.grade)
                else:
                    if subsection.optional:
                        #db().set_trace()
                        print('----------------')
                        print('')
                        print('group: %s' % group_with_rst.group_name)
                        print('   missing section: %s' % subsection.title)
                        total_missing += 1
                        print('')
                        print('----------------')
                        row_out.append(missing_val)
                    else:
                        msg = "did not find required grade %s" % \
                              subsection.title
                        raise ValueError, msg
            row_out.append(group_sec.grade)
        if total_missing > 1:
            print('*******************')
            print('')
            print('group: %s' % group_with_rst.group_name)
            print('  total missing subsections = %s' % total_missing)
            print('')
            print('*******************')
        return row_out


class design_report_grade_map_2011(proposal_grade_map_2011):
    def __init__(self):
        self.major_sections = []#you must do this before calling the _append* methods

        self._append_quick_read()
        self._append_introduction_and_prob_statement()
        #self._append_lit_review_and_back_res()

        self._append_design()
        self._append_analysis()
        self._append_misc()
        self._append_slow_read()


    def _append_design(self):
        title5 = 'Design'
        list5 = ['Design Methodology', \
                 'Completeness', \
                 'Quality of the Design', \
                 'Explanation', \
                 'Risks and Back-up Plans', \
                 ]
        #opt_list5 = []#'Design Strategy', 'Backup Plans']

        #self.append_optional(title5, list5, opt_list5)
        self.append_required([title5], [list5])


    def _append_analysis(self):
        title6 = 'Analysis'
        list6 = ['Preliminary Analysis and Feasibility Calculations', \
                 'Analysis Completed', \
                 'Explanation', \
                 'Connection to Decisions', \
                 'Thoroughness and Approach', \
                 ]
        #opt_list6 = ['Preliminary Analysis', 'Connection to Decisions']

        #self.append_optional(title6, list6, opt_list6)
        self.append_required([title6], [list6])


class final_report_grade_map_2012(design_report_grade_map_2011):
    def __init__(self):
        self.major_sections = []#you must do this before calling the _append* methods

        self._append_quick_read()
        self._append_introduction_and_prob_statement()
        self._append_design()
        self._append_analysis()
        self._append_prototype_construction()
        self._append_testing()
        self._append_misc()
        self._append_slow_read()


    def _append_introduction_and_prob_statement(self):
        title2 = 'Introduction and Problem Statement'
        list2 = ['Problem Statement and Formulation', \
                 'Design Goals', \
                 'Constraints']

        self.append_required([title2], [list2])


    def _append_design(self):
        title5 = 'Design'
        list5 = ['Design Methodology', \
                 'Quality of the Design', \
                 'Explanation', \
                 'Strengths and Weaknesses', \
                 ]
        #opt_list5 = []#'Design Strategy', 'Backup Plans']

        #self.append_optional(title5, list5, opt_list5)
        self.append_required([title5], [list5])


    def _append_analysis(self):
        title6 = 'Analysis'
        list6 = ['Thoroughness and Approach', \
                 'Explanation', \
                 'Connection to Decisions', \
                 ]
        #opt_list6 = ['Preliminary Analysis', 'Connection to Decisions']

        #self.append_optional(title6, list6, opt_list6)
        self.append_required([title6], [list6])


    def _append_prototype_construction(self):
        title6 = 'Prototype Construction'
        list6 = ['Discussion', \
                 'Challenges', \
                 'Modifications', \
                 ]
        self.append_required([title6], [list6])


    def _append_testing(self):
        title6 = 'Testing'
        list6 = ['Coverage and Appropriateness', \
                 'Methodology', \
                 'Presentation of Results', \
                 ]
        #opt_list6 = ['Preliminary Analysis', 'Connection to Decisions']

        #self.append_optional(title6, list6, opt_list6)
        self.append_required([title6], [list6])



class mini_project_report_map(proposal_grade_map_2011):
    def __init__(self):
        self.major_sections = []#you must do this before calling the _append* methods

        self._append_quick_read()
        self._append_introduction_and_bg_reading()
        self._append_design_methodology()
        self._append_analysis()
        self._append_final_design()
        self._append_budget()
        self._append_performance()
        self._append_conclussions()
        self._append_slow_read()


    def _append_introduction_and_bg_reading(self):
        mytitle = 'Introduction and Background Reading'
        mylist = ['Background Reading', \
                  'Definition of Engineering Design', \
                  'Convergent and Divergent Thinking', \
                  'The Role of Analysis', \
                  'What Did You Learn?', \
                 ]
        self.append_required([mytitle], [mylist])


    def _append_design_methodology(self):
        mytitle = 'Design Methodology'
        mylist = ['Discussion', \
                  'Validity of the Approach', \
                 ]
        self.append_required([mytitle], [mylist])


    def _append_analysis(self):
        mytitle = 'Analysis'
        mylist = ['Thoroughness and Approach', \
                  'Explanation', \
                  'Connection to Decisions', \
                 ]
        self.append_required([mytitle], [mylist])


    def _append_final_design(self):
        mytitle = 'Final Design'
        mylist = ['Explanation', \
                 ]
        self.append_required([mytitle], [mylist])


    def _append_budget(self):
        mytitle = 'Budget'
        mylist = ['Explanation', \
                 ]
        self.append_required([mytitle], [mylist])


    def _append_performance(self):
        mytitle = 'Performance'
        mylist = ['Explanation', \
                  'Expectations', \
                 ]
        self.append_required([mytitle], [mylist])


    def _append_conclussions(self):
        mytitle = 'Conclusions'
        mylist = ['Effectiveness', \
                 ]
        self.append_required([mytitle], [mylist])





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


    def get_grades(self):
        grade_dict = {}
        for key, weight in self.weight_dict.iteritems():
            cursec = self.find_section(key)
            grade_dict[key] = cursec.grade
        self.grades = grade_dict


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


    def build_spreadsheet_row(self, look_for_penalty=False, \
                              grade_map=None):
        row_out = [self.get_group_name_from_path()]
        if grade_map is None:
            for section in self.sec_list:
                row_out.extend(section.get_grades())
        else:
            #intelligently map the grades, allowing certain ones to be
            #blank
            cur_grades = grade_map.build_row(self)
            row_out.extend(cur_grades)
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


    def _compose_and_send_team_gmail(self, subject, body, debug=0, \
                                     attach_sig=True):
        if not hasattr(self,'pdfpath'):
            print('you must call pres_rst_parser.rst_team before sending team email')
            return
        if not os.path.exists(self.pdfpath):
            print('pdf does not exist: '+self.pdfpath)
            return
        
        if debug:
            emails = ['ryanlists@gmail.com']
        else:
            emails = self.emails

        if attach_sig:
            body += '\n' + mysig
            
        gmail_smtp.sendMail(emails, subject, body, self.pdfpath)



    def compose_and_send_team_gmail(self, subject, debug=0):#, ga):
        """ga is a gmail account instance from libgmail that has
        already been logged into."""

        body = "The attached pdf contains your team grade and my feedback."
        
        self._compose_and_send_team_gmail(subject, body, debug=debug)




    def find_section(self, title):
        for sec in self.sec_list:
            if sec.title == title:
                return sec


class group_rst_needing_grade_correction(group_with_rst):
    """This class exists to cleanly correct the grades in an rst.  The
    need for this comes from having guests/volunteers grade half of
    the design review presentations for 482.  This class will take an
    rst path and a correction dict, open the rst, read in the grades,
    multiply the grade for each section by the correction factor for
    that section from the dictionary, and then output modified rst to
    a new folder."""
    def __init__(self, pathin, correction_dict={}, outfolder=None, \
                 **kwargs):
        group_with_rst.__init__(self, pathin, **kwargs)
        self.correction_dict = correction_dict
        curfolder, name = os.path.split(pathin)
        self.name = name
        if outfolder is None:#add corrected folder to pathin
            curfolder, name = os.path.split(pathin)
            outfolder = os.path.join(curfolder, 'corrected')
            if not os.path.exists(outfolder):
                os.mkdir(outfolder)
        self.outfolder = outfolder
        self.outpath = os.path.join(self.outfolder, name)


    def save_rst(self):
        #self.get_rst_name()
        txt_mixin.dump(self.outpath, self.corrected_rst)


    def calc_correct_grades(self):
        self.corrected_grades = {}
        for key, value in self.correction_dict.iteritems():
            raw_grade = self.grades[key]
            corrected_grade = raw_grade*value
            self.corrected_grades[key] = corrected_grade


    def build_corrected_rst_output(self):
        if not hasattr(self, 'corrected_grades'):
            self.calc_correct_grades()
        self.corrected_rst = copy.copy(self.header)
        for cur_sec in self.sec_list:
            self.corrected_rst.append('')
            self.corrected_rst.append(cur_sec.title)
            self.corrected_rst.append(cur_sec.dec_line)
            key = cur_sec.title
            if self.corrected_grades.has_key(key):
                #newgrade = self.corrected_grades[key]
                factor = self.correction_dict[key]
                cur_sec.correct_grade(factor)
            self.corrected_rst.extend(cur_sec.content)
            ## if cur_sec.title == 'Timing':
            ##     self.corrected_rst.append('')
            ##     self.corrected_rst.append('**Timing Penalty:** %0.4g' % \
            ##                          self.time_penalty)
            self.corrected_rst.append('')
        self.corrected_rst.append('')
        ## overall_title = mysecdec('Overall Grade')
        ## self.corrected_rst.extend(overall_title)
        ## self.corrected_rst.append(':grade:`%0.3g`' % self.overall_grade)

weight_dict_proposal_2011 = {'Writing: Quick Read':0.10, \
                             'Introduction and Problem Statement':0.2, \
                             'Literature Review and Background Research':0.05, \
                             'Contemporary Issues':0.05, \
                             'Design Strategy': 0.2, \
                             'Analysis': 0.2, \
                             'Miscellaneous': 0.05, \
                             'Writing: Slow Read':0.15, \
                             #'Extra Credit':group_rst_parser.extra_credit, \
                             #'Penalty':1.0,\
                             }

proposal_ordered_keys = ['Writing: Quick Read', \
                         'Introduction and Problem Statement', \
                         'Literature Review and Background Research', \
                         'Contemporary Issues', \
                         'Design Strategy', \
                         'Analysis', \
                         'Miscellaneous', \
                         'Writing: Slow Read', \
                         ]


class proposal(group_with_rst):
    def __init__(self, pathin, weight_dict=weight_dict_proposal_2011, \
                 ordered_keys=proposal_ordered_keys, \
                 **kwargs):
        group_with_rst.__init__(self, pathin, **kwargs)
        self.weight_dict = weight_dict
        self.ordered_keys = ordered_keys


    def calc_overall_score(self):
        self.overall_grade = 0.0
        for key, weight in self.weight_dict.iteritems():
            cursec = self.find_section(key)
            if cursec is not None:
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


    def build_team_rst_output_old(self):
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

        line_fmt = '& + %0.2g (\\textrm{%s}) \\\\'
        line_fmt2 = '& + \\left. %0.2g (\\textrm{%s}) \\right) \\\\'
        def line_out(weight, title, wa=True, last=False):
            if wa:
                title += ' Weighted Average'
            if last:
                myline = line_fmt2 % (weight, title)
            else:
                myline = line_fmt % (weight, title)
            eq_out(myline)

        eq_out('\\newcommand{\\myrule}{\\rule{0pt}{1EM}}')
        eq_out(r'\begin{equation*}\begin{split}')
        ## eq_out(r'\textrm{grade} = & 10 \left( \myrule 0.05(\textrm{Contemporary Issues}) \right. \\')
        ## eq_out(r'& + 0.15 (\textrm{Quick Read Weighted Average}) ')
        ## eq_out(r'+ 0.25 (\textrm{Slow Read Weighted Average}) \\')
        ## eq_out(r'& \left. + 0.5 (\textrm{Content Weighted Average}) \myrule \right)')
        eq_out(r'\textrm{grade} = & 10 \left( \myrule 0.1 (\textrm{Quick Read Weighted Average}) \right. \\')
        line_out(0.20,'Introduction and Problem Statement')
        eq_out(r'& + 0.05 (\textrm{Literature Review and Background Research Weighted Average}) \\')
        eq_out(r'& + 0.05 (\textrm{Contemporary Issues}) \\')
        line_out(0.2, 'Design Strategy')
        line_out(0.2, 'Analysis')
        line_out(0.05, 'Miscellaneous')
        line_out(0.15, 'Slow Read', last=True)

        if self.penalty is not None:
            eq_out(r'\times (1 + \textrm{Penalty}/100)')
        eq_out(r'\end{split}\end{equation*}')
        self.team_rst.append('')
        self.team_rst.append('')
        self.team_rst.append(':grade:`%0.1f`' % self.overall_grade)


    def append_eqn_rst(self):
        ## formula_line = '10*(0.5*(Contemporary Issues) + ' + \
        ##                '0.2*(Quick Read Weighted Average) + ' + \
        ##                '0.25*(Slow Read Weighted Average) + ' + \
        ##                '0.5*(Content Weighted Average))'
        ## if self.penalty is not None:
        ##     formula_line += '* (1 + penalty/100)'
        self.team_rst.append('**Formula:**')
        self.team_rst.append('')
        self.team_rst.append('.. raw:: latex')
        self.team_rst.append('')
        ws = ' '*4
        out = self.team_rst.append
        def eq_out(strin):
            out(ws + strin)

        line_fmt = '& + %0.2g (\\textrm{%s}) \\\\'
        line_fmt2 = '& + \\left. %0.2g (\\textrm{%s}) \\myrule \\right) \\\\'
        def line_out(weight, title, wa=True, last=False):
            if wa:
                title += ' Weighted Average'
            if last:
                myline = line_fmt2 % (weight, title)
            else:
                myline = line_fmt % (weight, title)
            eq_out(myline)

        eq_out('\\newcommand{\\myrule}{\\rule{0pt}{1EM}}')
        eq_out(r'\begin{equation*}\begin{split}')
        ## eq_out(r'\textrm{grade} = & 10 \left( \myrule 0.05(\textrm{Contemporary Issues}) \right. \\')
        ## eq_out(r'& + 0.15 (\textrm{Quick Read Weighted Average}) ')
        ## eq_out(r'+ 0.25 (\textrm{Slow Read Weighted Average}) \\')
        ## eq_out(r'& \left. + 0.5 (\textrm{Content Weighted Average}) \myrule \right)')
        first = 1
        N = len(self.ordered_keys)
        for i, key in enumerate(self.ordered_keys):
            weight = self.weight_dict[key]
            if first:
                first = 0
                eq_out(r'\textrm{grade} = 10 & \left( \myrule \right. %s (\textrm{%s}) \\' % (weight, key))
            else:
                last = False
                if i == N-1:
                    last = True
                line_out(weight, key, last=last)

        if self.penalty is not None:
            eq_out(r'\times (1 + \textrm{Penalty}/100)')
        eq_out(r'\end{split}\end{equation*}')


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
        self.append_eqn_rst()
        self.team_rst.append('')
        self.team_rst.append('')
        self.team_rst.append(':grade:`%0.1f`' % self.overall_grade)


    def compose_and_send_team_gmail(self):#, subject):#, ga):
        self.pdfpath_checker()
        subject = "ME 482: Proposal Grade"
        body = "The attached pdf contains your team proposal grade and my feedback."

        gmail_smtp.send_mail_siue(self.emails, subject, body, self.pdfpath)



weight_dict_design_report_2011 = {'Writing: Quick Read':0.10, \
                                  'Introduction and Problem Statement':0.2, \
                                  'Design': 0.25, \
                                  'Analysis': 0.25, \
                                  'Miscellaneous': 0.05, \
                                  'Writing: Slow Read':0.15, \
                                  #'Extra Credit':group_rst_parser.extra_credit, \
                                  #'Penalty':group_rst_parser.penalty, \
                                  }

design_report_ordered_keys = ['Writing: Quick Read', \
                              'Introduction and Problem Statement', \
                              'Design', \
                              'Analysis', \
                              'Miscellaneous', \
                              'Writing: Slow Read', \
                              ]



class design_report(proposal):
    def __init__(self, pathin, weight_dict=weight_dict_design_report_2011, \
                 ordered_keys=design_report_ordered_keys, \
                 **kwargs):
        proposal.__init__(self, pathin, weight_dict=weight_dict, \
                          ordered_keys=ordered_keys, \
                          **kwargs)

    def compose_and_send_team_gmail(self):#, subject):#, ga):
        self.pdfpath_checker()
        subject = "ME 482: Design Report Grade"
        body = "The attached pdf contains your team proposal grade and my feedback."

        gmail_smtp.send_mail_siue(self.emails, subject, body, self.pdfpath)

#---------------------------------
#
# Final report 2012
#
#---------------------------------
weight_dict_final_report_2012 = {'Writing: Quick Read':0.1, \
                                 'Introduction and Problem Statement':0.1, \
                                 'Design': 0.2, \
                                 'Analysis': 0.2, \
                                 'Prototype Construction': 0.1, \
                                 'Testing': 0.1, \
                                 'Miscellaneous': 0.05, \
                                 'Writing: Slow Read':0.15, \
                                  #'Extra Credit':group_rst_parser.extra_credit, \
                                  #'Penalty':group_rst_parser.penalty, \
                                 }

final_report_ordered_keys = ['Writing: Quick Read', \
                             'Introduction and Problem Statement', \
                             'Design', \
                             'Analysis', \
                             'Prototype Construction', \
                             'Testing', \
                             'Miscellaneous', \
                             'Writing: Slow Read', \
                             ]



class final_report(design_report):
    def __init__(self, pathin, weight_dict=weight_dict_final_report_2012, \
                 ordered_keys=final_report_ordered_keys, \
                 **kwargs):
        design_report.__init__(self, pathin, weight_dict=weight_dict, \
                               ordered_keys=ordered_keys, \
                               **kwargs)


    def compose_and_send_team_gmail(self):#, subject):#, ga):
        self.pdfpath_checker()
        subject = "ME 484: Final Report Grade"
        body = "The attached pdf contains your team proposal grade and my feedback."

        gmail_smtp.sendMail(self.emails, subject, body, self.pdfpath)


weight_dict_mini_project = {'Writing: Quick Read':0.1, \
                            'Introduction and Background Reading':0.1, \
                            'Design Methodology':0.15, \
                            'Analysis':0.2, \
                            'Final Design':0.1, \
                            'Budget':0.1, \
                            'Performance':0.05, \
                            'Conclusions':0.05, \
                            'Writing: Slow Read':0.15, \
                            }

mini_project_ordered_keys = ['Writing: Quick Read', \
                             'Introduction and Background Reading', \
                             'Design Methodology', \
                             'Analysis', \
                             'Final Design', \
                             'Budget', \
                             'Performance', \
                             'Conclusions', \
                             'Writing: Slow Read', \
                             ]


class mini_project_report(design_report):
    def __init__(self, pathin, weight_dict=weight_dict_mini_project, \
                 ordered_keys=mini_project_ordered_keys, \
                 **kwargs):
        design_report.__init__(self, pathin, weight_dict=weight_dict, \
                               ordered_keys=ordered_keys, \
                               **kwargs)


    def compose_and_send_team_gmail(self, debug=0):#, subject):#, ga):
        """ga is a gmail account instance from libgmail that has
        already been logged into."""

        subject = 'ME 482: Mini-Project Grade'
        body = "The attached pdf contains your team grade and my feedback " + \
               "for the mini-project written report."
        self._compose_and_send_team_gmail(subject, body, debug=debug)

    
#---------------------------------


pres_weight_w_apperance_2011 = {'Appearance':0.05,\
                                'Content and Organization':0.45, \
                                'Speaking and Delivery':0.3, \
                                'Slides':0.1,\
                                'Listening to and Answering Questions':0.1}



class presentation_with_appearance(group_with_rst):
#    Appearance
#    Content and Organization
#    Speaking and Delivery
#    Slides
#    Listening to and Answering Questions

    def __init__(self, pathin, max_time=15.0, \
                 min_time=5.0, grace=0.25, \
                 **kwargs):
        group_with_rst.__init__(self, pathin, **kwargs)
        self.max_time = max_time
        self.min_time = min_time
        self.grace = grace

        if kwargs.has_key('weight_dict'):
            weight_dict = kwargs['weight_dict']
        else:
            weight_dict = pres_weight_w_apperance_2011
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
        if time > (self.max_time + self.grace):
            num_steps = int((time-self.max_time)/0.25)
            penalty = -0.075*num_steps
        elif time < (self.min_time - self.grace):
            num_steps = int((self.min_time-time)/0.25)
            penalty = -0.075*num_steps
        else:
            penalty = 0.0
        self.time_penalty = penalty



class presentation_needing_grade_correction(group_rst_needing_grade_correction):
    def __init__(self, *args, **kwargs):
        #group_with_rst.__init__(self, *args, **kwargs)
        group_rst_needing_grade_correction.__init__(self, *args, **kwargs)
        self.weight_dict = pres_weight_w_apperance_2011


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


    def _check_time_NA(self, time_lines):
        if len(time_lines) == 1:
            time_str = time_lines[0]
            if time_str.lower() == 'na':
                return True
        return False


    def get_timing_grade(self):
        time_lines = self.get_time_lines()
        if self._check_time_NA(time_lines):
            self.time_penalty = 0
            return
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



class proposal_presentation_no_appearance(update_presentation):
    def get_timing_grade(self):
        time_lines = self.get_time_lines()
        time_str = self.find_time_string(time_lines)
        time = self.parse_time_string(time_str)
        penalty = 0.0
        if time > 11.251:
            num_steps = int((time-11.0)/0.25)
            penalty = -0.075*num_steps
        elif time < 8.849:
            num_steps = int((9.0-time)/0.25)
            penalty = -0.075*num_steps
        self.time_penalty = penalty


class mini_project_presentation(update_presentation):
    def get_timing_grade(self):
        time_lines = self.get_time_lines()
        time_str = self.find_time_string(time_lines)
        time = self.parse_time_string(time_str)
        penalty = 0.0
        if time > 5.51:
            num_steps = int((time-5.51)/0.5)
            penalty = -0.1*num_steps
        elif time < 3.5:
            num_steps = int((3.5-time)/0.5)
            penalty = -0.1*num_steps
        self.time_penalty = penalty


    def compose_and_send_team_gmail(self, subject, debug=0):#, subject):#, ga):
        body = "The attached pdf contains your team grade and my feedback " + \
               "for the mini-project presentation."
        self._compose_and_send_team_gmail(subject, body, debug=debug)
