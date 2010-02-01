import txt_mixin, spreadsheet, rst_creator, rwkos
import re, os
import gmail_smtp
reload(gmail_smtp)

from scipy import mean

from IPython.Debugger import Pdb

grade_pat = re.compile(':grade:`(.*)`')

timing_pat = re.compile('^Tim(ing|e)[: ]*$')
notes_pat = re.compile('^Notes*[: ]*$')

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

group_dir = rwkos.FindFullPath('siue/classes/482/2009/group_grades')
group_name = 'group_list.csv'
group_path = os.path.join(group_dir, group_name)
group_list_482_F09 = spreadsheet.group_list(group_path)
email_path = rwkos.FindFullPath('siue/classes/482/2009/class_list.csv')
email_list = spreadsheet.email_list(email_path)

class section(txt_mixin.txt_list):
    def __init__(self, raw_list):
        #print('raw_list=')
        #print('\n'.join(raw_list))
        self.title = raw_list.pop(0)
        self.dec_line = raw_list.pop(0)
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
        
    def __repr__(self):
        outstr = self.title+'\n' + \
                 self.dec_line +'\n'+ \
                 '\n'.join(self.content)
        return outstr

from fall_2009_482 import alts as alts_F482

#alts = {'Trutter':'Ben','Herren':'Zach', 'Schelp':'Tim', \
#        'Tolbert':'Chris', 'Bailey':'Matt'}

class member(object):
    def __init__(self, lastname, firstname, email):
        self.lastname = lastname
        self.firstname = firstname
        self.email = email
        
    
class speaker(object):
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

        
class pres_rst_parser(txt_mixin.txt_file_with_list):
    def __init__(self, filepath, group_list=None, alts=None):
        txt_mixin.txt_file_with_list.__init__(self, filepath)
        #Pdb().set_trace()
        if group_list is None:
            self.group_list = group_list_482_F09
        else:
            self.group_list = group_list
        if alts is None:
            self.alts = alts_F482
        else:
            self.alts = alts
        self.break_into_sections()
        self.get_group_name_from_path()
        self.get_timing_grade()
        self.find_members()
        self.pop_notes()
        self.get_section_labels()        
        
        
    def get_group_name_from_path(self):
        folder, filename = os.path.split(self.pathin)
        fno, ext = os.path.splitext(filename)
        self.group_name = fno.replace('_',' ')
        return self.group_name

    def _tweak_header(self):
        if '.. role:: grade' not in self.header:
            self.header.append('')
            self.header.append('.. role:: grade')
            self.header.append('')
            

    def break_into_sections(self, pat='^-+$'):
        inds = self.findallre(pat)
        inds2 = [item-1 for item in inds]
        inds2.append(None)
        self.raw_sec_list = None
        prevind = inds2.pop(0)
        self.header = self.list[0:prevind]
        self._tweak_header()
        for ind in inds2:
            curlist = self.list[prevind:ind]
            if self.raw_sec_list is None:
                self.raw_sec_list = [curlist]
            else:
                self.raw_sec_list.append(curlist)
            prevind = ind
        self.sec_list = None

        for curlist in self.raw_sec_list:
            cur_sec = section(curlist)
            if self.sec_list is None:
                self.sec_list = [cur_sec]
            else:
                self.sec_list.append(cur_sec)

    def _build_sec_titles(self):
        self.title_list = [section.title for section in self.sec_list]

    def search_sections(self, title):
        for n, section in enumerate(self.title_list):
            if section == title:
                return n
        return -1

    def get_time_lines(self):
        time_titles = ['Timing','Time']
        for n, section in enumerate(self.sec_list):
            q = timing_pat.search(section.title)
            if q:
                self.time_ind = n + 1#plus one because group name will
                                     #be in the first column
                return section.content

        
    def get_speaking_lines(self):
        for n, section in enumerate(self.sec_list):
            if section.title == 'Speaking and Delivery':
                self.speaking_ind = n + 1#plus one because group name will
                                     #be in the first column
                return section.content

    def pop_notes(self):
        self.notes = None
        for n, section in enumerate(self.sec_list):
            q1 = notes_pat.search(section.title)
            if q1:
                self.notes = self.sec_list.pop(n)
                break
                

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
        if time_str is None:
            self.time_penalty = 0.0
        else:
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
            labels.append(section.title)
        self.labels = labels
        self.labels.append('Overall Score')
        self.labels.insert(self.time_ind+1, 'Timing Penalty')
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
        self.ave = mean(grades) + self.time_penalty
        return self.ave


    def build_spreadsheet_row(self):
        row_out = [self.get_group_name_from_path()]
        for section in self.sec_list:
            if hasattr(section,'grade'):
                elem = str(section.grade)
            else:
                elem = ';'.join(section.content)
            row_out.append(elem)
        self.calc_overall_score()
        row_out.append(self.ave)
        row_out.insert(self.time_ind+1, self.time_penalty)
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
            qt = timing_pat.search(cur_sec.title)
            if qt:
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
            email = email_list.get_email(last)
            curmember = member(last, first, email)
            if members is None:
                members = {first:curmember}
            else:
                members[first] = curmember
        self.members = members
        self.emails = email_list.get_emails(lastnames)
        return self.emails
        

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

class update_pres_parser(pres_rst_parser):
    def get_timing_grade(self, max_t=7.0, min_t=5.0, grace=0.25):
        time_lines = self.get_time_lines()
        time_str = self.find_time_string(time_lines)
        if time_str is None:
            self.time_penalty = 0.0
        else:
            time = self.parse_time_string(time_str)
            if time > (max_t + grace):
                num_steps = int((time-max_t-grace)/0.5+0.95)
                penalty = -0.1*num_steps
            elif time < (min_t - grace):
                num_steps = int((min_t-grace-time)/0.5+0.95)
                penalty = -0.1*num_steps
            else:
                penalty = 0.0
            self.time_penalty = penalty
        
    
def myfilt(pathin):
    folder, filename = os.path.split(pathin)
    if filename.lower() == 'order.rst':
        return 0
    else:
        return 1
    
        
if __name__ == '__main__':
    from optparse import OptionParser

    import sys, os


    usage = 'usage: %prog [options] folder subject'
    parser = OptionParser(usage)


    parser.add_option("-r", "--runlatex", dest="runlatex", \
                      help="Run LaTeX after presentation is converted to tex.", \
                      default=1, type="int")

    parser.add_option("-s", "--send", dest="send", \
                      help="send pdfs via email", \
                      default=0, type="int")

    import libgmail
    import copy
    from getpass import getpass

    ## parser.add_option("-n", "--name", dest="name", \
    ##                   help="Presentation name.", \
    ##                   default='', type="string")


    (options, args) = parser.parse_args()

    folder = args[0]
    subject = args[1]
    full_subject = "ME 482 Grade: " + subject
    individual_subject = "ME 482 Individual Speaking Grade: " + subject

    
    import glob

    pat = os.path.join(folder, '*.rst')
    paths = glob.glob(pat)

    paths = filter(myfilt, paths)
    
    sendmail = options.send

##     if sendmail:
##         #    pw = getpass("Password: ")
##         pw='Mustard Seed?!?!'
##         ga = libgmail.GmailAccount('ryanwkrauss@gmail.com',pw)
##         ga.login()

##         mycontacts = ga.getContacts()

    csv_name = subject.replace(' ','_')
    csv_name = csv_name.replace('.','_')
    csv_name = csv_name.replace('__','_')
    csv_name += '.csv'
    csv_outpath = os.path.join(folder,csv_name)#'presentation_grades.csv')
    
    rst_out_dir = 'team_rst_output'
    out_dir = os.path.join(folder, rst_out_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    nested_list = None
    for curpath in paths:
        print('==================')
        print('curpath='+str(curpath))
        #curfile = pres_rst_parser(curpath)
        curfile = update_pres_parser(curpath)
        currow = curfile.build_spreadsheet_row()
        if nested_list is None:
            first_row = curfile.get_section_labels()
            nested_list = [currow]
        else:
            nested_list.append(currow)
        curfile.build_team_rst_output()
        junk, inname = os.path.split(curpath)
        fno, ext = os.path.splitext(inname)
        outname = fno +'_team_out.rst'
        outpath = os.path.join(out_dir, outname)
        curfile.save_team_rst(outpath)
        curfile.build_speaking_rst(runlatex=options.runlatex)
        if options.runlatex:
            curfile.rst_team()
        else:
            curfile.set_pdfpath()

        test = 1
        if test:
            print(curfile.group_name)
            print('team emails = ' + str(curfile.emails))
            for curspeaker in curfile.speaker_list:
                print(curspeaker.name + ':' + str(curspeaker.email))
            print('-----------')
            for key, student in curfile.members.iteritems():
                print(key + ':' + str(student.email))
        if sendmail:
            curfile.compose_and_send_team_gmail(full_subject)
            for curspeaker in curfile.speaker_list:
                curspeaker.send_email(individual_subject)
        
    spreadsheet.WriteMatrixtoCSV(nested_list, csv_outpath, labels=first_row)
