import os
import txt_mixin, spreadsheet

from IPython.Debugger import Pdb

class class_list_maker(txt_mixin.txt_file_with_list):
    def replace_tabs(self):
        self.list.replaceall('\t',',')


    def clean_end_of_lines(self):
        self.list.replaceallre(',Register.*','')


    def clean_number_from_front(self):
        self.list.replaceallre('^[0-9]+,','')
        

    def clean_spaces(self):
        self.list.replaceallre(' *, *',',')

        
    def pop_blanks(self):
        last = ''
        while not last:
            last = self.list.pop()
        self.list.append(last)
        

    def insert_labels(self):
        self.list.insert(0,'Lastname,Firstname,student ID')


    def drop_confidentials(self):
        self.list.replaceall(' Confidential','')
        

    def run(self, pathout=None):
        self.replace_tabs()
        self.clean_end_of_lines()
        self.clean_number_from_front()
        self.pop_blanks()
        self.insert_labels()
        self.drop_confidentials()
        self.clean_spaces()
        if pathout is not None:
            self.save(pathout)
        


class class_list_for_emails(spreadsheet.CSVSpreadSheet):
    def __init__(self, pathin, emails):
        mymap = {'Lastname':'lastname', \
                 'Firstname':'firstname', \
                 'student ID':'ID'}
        spreadsheet.CSVSpreadSheet.__init__(self, pathin, colmap=mymap)
        labels=['Lastname','Firstname']
        self.FindLabelRow(labels)
        self.MapCols()
        self.emails_in = emails


    def try_one_email(self, strin):
        ind_list = self.emails_in.findall(strin)
        if len(ind_list) == 1:
            return True
        else:
            return False


    def find_one_email(self, first, last, verbosity=1):
        N = 7
        nf = len(first)
        nl = len(last)
        if last == 'Bemrose-Fetter':
            return 'rbemros@siue.edu'
        for i in range(nf):
            curfirst = first[0:i+1]
            n = N-len(curfirst)
            if n > nl:
                curlast = last
            else:
                curlast = last[0:n]
            curstr = curfirst + curlast
            curstr = curstr.lower()
            if verbosity > 2:
                print('searching for: ' + curstr)
            mybool = self.try_one_email(curstr)
            if mybool:
                myind = self.emails_in.findall(curstr)[0]
                curemail = self.emails_in[myind]
                if verbosity > 1:
                    print('found: ' + str(curemail))
                return curemail
            
        if verbosity > 0:
            # we would only get this far if we did not find the email at all
            print('did not find email for: ' + first + ' ' + last)


    def find_all_emails(self):
        emails_out = []    
        for last, first in zip(self.lastname, self.firstname):
            first = first.strip()
            last = last.strip()
            curemail = self.find_one_email(first, last)
            if curemail:
                emails_out.append(curemail)
            else:
                emails_out.append('')
        self.emails_out = emails_out
        self.AppendCol('Emails',self.emails_out)        
        return emails_out


    def add_note(self, note):
        N = len(self.lastname)
        self.AppendCol('Note', [note]*N)


    def save(self, pathout):
        self.WriteDataCSV(pathout)


def load_email_list(pathin):
    f = open(pathin)
    lines = f.readlines()
    f.close()
    stringin = ', '.join(lines)
    stringin = stringin.strip()
    mylist = stringin.split(',')
    clean_list = [item.strip() for item in mylist]
    out_list = txt_mixin.txt_list(clean_list)
    return out_list

        
if __name__ == '__main__':
    case = 2
    if case == 1:
        root = '/home/ryan/siue/classes/mechatronics/2010'
        note = 'ME458 Fall 2010'
    elif case == 2:
        root = '/home/ryan/siue/classes/482/2010'
        note = 'ME482 Fall 2010'

    pathin = os.path.join(root, 'class_list_raw.csv')
    pathout = pathin.replace('_raw.csv','_out.csv')
    email_path = os.path.join(root, 'email_list_raw.csv')
    mylist = class_list_maker(pathin)
    mylist.run(pathout)
    emails = load_email_list(email_path)
    class_list = class_list_for_emails(pathout, emails)
    class_list.find_all_emails()
    class_list.add_note(note)
    final_path = os.path.join(root, 'class_list_with_mapped_emails.csv')
    class_list.save(final_path)
    
