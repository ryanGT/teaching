import txt_database, re, txt_mixin
from numpy import array
import copy

class email_list(txt_database.txt_database):
    """A spreadsheet class for looking up emails in a class list.
    Typically, there is one row of labels and the first two columns
    contain student names and emails.  The zeroth column is assumed to
    contain lastnames.  The next column is checked for firstnames.  A
    column whose labels.lower() contains 'email' is the email column."""
    def look_for_first_names(self):
        first_name_col = self.find_col_from_list(['firstname','first name', \
                                                 'fname', 'firstnames', \
                                                 'first names','fnames'])
        if first_name_col is not None:
            self.first_names = self.data[:,first_name_col]
            self.first_name_col = first_name_col
            found_first = True
        else:
            found_first = True

        return found_first


    def get_names(self):
        last_name_col = self.find_col_from_list(['lastname','last name', \
                                                 'lname', 'lastnames', \
                                                 'last names','lnames'])
        self.last_names = self.data[:,last_name_col]
        self.last_name_col = last_name_col
        
        has_first = self.look_for_first_names()
        if has_first:
            names = []
            for first, last in zip(self.first_names, self.last_names):
                curname = last + ', ' + first
                names.append(curname)
            self.names = txt_mixin.txt_list(copy.copy(names))

        else:
            self.names = txt_mixin.txt_list(copy.copy(self.last_names))


    def find_emails(self):
        email_col = self.find_col_from_list(['email','emails'])
        self.email_col = email_col
        self.emails = self.data[:,email_col]
        return self.email_col


    def __init__(self, pathin):
        data, labels = txt_database._open_txt_file(pathin)
        txt_database.txt_database.__init__(self, data, labels)
        self.get_names()
        self.find_emails()


    def get_email(self, lastname, firstname=None, aslist=False, \
                  fail_quietly=False):
        """Search for email in list using lastname or lastname,
        firstname.  aslist=True forces email to be returned in list
        even if it is only one address.  Students can have more than
        one list if the entry in that column is delimited by [,; ]."""
        p = re.compile('[,; ]+')
        name = lastname
        if firstname is not None:
            name += ', '+firstname
        inds = self.names.findall(name)
        if not fail_quietly:
            assert len(inds)==1, "Did not find exactly one match for %s, %s.  len(inds)=%i" % \
                  (lastname, firstname, len(inds))
        if len(inds) == 0:
            print('did not find %s in self.names' % name)
        if len(inds) > 1:
            print('found more than 1 %s in self.names' % name)
        email = self.emails[inds[0]]
        email = email.strip()
        q = p.search(email)
        if q or aslist:
            return p.split(email)
        else:
            return email

    def get_emails(self, lastnames, firstnames=None):
        if firstnames is None:
            firstnames = [None]*len(lastnames)
        email_list = None
        for lastname, firstname in zip(lastnames, firstnames):
            curemails = self.get_email(lastname, firstname, aslist=1)
            if email_list is None:
                email_list = curemails
            else:
                email_list.extend(curemails)
        return email_list

