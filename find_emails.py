from scipy import *
import spreadsheet
mymap = {'Lastname':'lastname','Firstname':'firstname','student ID':'ID', '356':'ME356'}
mysheet = spreadsheet.CSVSpreadSheet('class_list.csv',colmap=mymap)
labels=['Lastname','Firstname']
mysheet.FindLabelRow(labels)
mysheet.MapCols()


import txt_mixin

emails = txt_mixin.txt_file_with_list('email_addresses.csv')

def try_one_email(strin):
    ind_list = emails.findall(strin)
    if len(ind_list) == 1:
        return True
    else:
        return False

    
def find_email(first, last, verbosity=1):
    N = 7
    nf = len(first)
    nl = len(last)
    for i in range(nf):
        curfirst = first[0:i+1]
        n = N-len(curfirst)
        if n > nl:
            curlast = last
        else:
            curlast = last[0:n]
        curstr = curfirst + curlast
        curstr = curstr.lower()
        if verbosity > 0:
            print('searching for: ' + curstr)
        mybool = try_one_email(curstr)
        if mybool:
            myind = emails.findall(curstr)[0]
            curemail = emails.list[myind]
            if verbosity > 0:
                print('found: ' + str(curemail))
            return curemail
        
        
        
emails_out = []    
for last, first in zip(mysheet.lastname, mysheet.firstname):
    first = first.strip()
    last = last.strip()
    curemail = find_email(first, last)
    if curemail:
        emails_out.append(curemail)
    else:
        emails_out.append('')


mysheet.AppendCol('Emails',emails_out)
mysheet.WriteDataCSV('class_list_with_mapped_emails.csv')
