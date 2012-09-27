import spreadsheet, txt_mixin, os, misc_utils
from numpy import column_stack, row_stack, unique

import class_list_maker

poplist = ['Student Name']


## To Do:

##  - I am not actually reading in the team numbers and
##  auto-generating the final file for now.  I already have a mostly
##  complete spreadsheet file that just needs banner ids and emails.


class catme_sheet(spreadsheet.TabDelimSpreadSheet):
    def _load_emails(self):
        raw_list = txt_mixin.txt_file_with_list(self.raw_email_filename)
        emails = raw_list.list[0].split(',')
        emails = [item.strip() for item in emails]
        mylist = txt_mixin.txt_list(emails)
        self.emails = mylist

        
    def __init__(self, filename, raw_email_filename):
        spreadsheet.TabDelimSpreadSheet.__init__(self, filename)
        self.raw_email_filename = raw_email_filename
        self._load_emails()
        self.ReadData()
        self.names = self.get_col(1)
        self.ids = self.get_col(2)
        if self.names[0] in poplist:
            self.names.pop(0)
        if self.ids[0].lower() == 'id':
            self.ids.pop(0)
        self.lastnames, self.firstnames = class_list_maker.split_names(self.names)
        self.last4 = [item[-4:] for item in self.ids]
        self.last5 = [item[-5:] for item in self.ids]
        temp = unique(self.last4)
        assert len(temp) == len(self.last4), 'uniqueness problem with last4'
        self.find_all_emails()
        

    def find_one_email(self, lastname, firstname):
        last = lastname.lower()
        first = firstname.lower()

        Nf = len(first)

        i = 1

        N = 7

        while i < Nf:
            fi = first[0:i]
            full = fi + last
            if len(full) > N:
                full = full[0:N]

            inds = self.emails.findall(full)
            if not inds:
                i += 1
            else:
                if len(inds) > 1:
                    matchstr = ''
                    for ind in inds:
                        matchstr += self.emails[ind] + ' '
                assert len(inds) == 1, 'Found more than one match for %s, matches: %s' % (full, matchstr)
                return self.emails[inds[0]]


    def find_all_emails(self):
        sorted_emails = []


        for last, first in zip(self.lastnames, self.firstnames):
            cur_email = self.find_one_email(last, first)
            sorted_emails.append(cur_email)

        self.sorted_emails = sorted_emails
        

    def dump(self, filename, attrlist=None, labels=None):
        if attrlist is None:
            attrlist = ['lastnames','firstnames','last4','sorted_emails']
        if labels is None:
            labels = ['last','first','id','email']
            
        vect_list = []
        for attr in attrlist:
            cur_vect = getattr(self, attr)
            vect_list.append(cur_vect)

            misc_utils.dump_vectors(filename, \
                                    vect_list, labels, fmt='%s', delim=',')
        

        
if __name__ == '__main__':
    mypath = '/home/ryan/siue/classes/IME_106/2012/class_list_sec1.txt'
    email_path = '/home/ryan/siue/classes/IME_106/2012/raw_email_list.txt'
    mysheet = catme_sheet(mypath,email_path)
    dumppath = '/home/ryan/siue/classes/IME_106/2012/sec1_catme_mostly_complete.csv'
    mysheet.dump(dumppath)
    
