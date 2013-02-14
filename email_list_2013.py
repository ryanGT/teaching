import txt_database, txt_mixin

class email_list(txt_database.txt_database):
    def __init__(self, pathin):
        data, labels = txt_database._open_txt_file(pathin)
        txt_database.txt_database.__init__(self, data, labels)
        self.last_name_list = txt_mixin.txt_list(self.Last_Name)
        self.first_name_list = txt_mixin.txt_list(self.First_Name)
        

    def find_email(self, lastname, firstname=None):
        #last_inds = self.last_name_list.findall(lastname)
        bv = self.search_attr_exact_match('Last_Name', lastname)
        if not bv.any():
            raise KeyError, "could not find a match for lastname %s" % lastname
        else:
            filt_db = self.filter(bv)
            nr, nc = filt_db.data.shape
            if nr == 1:
                return str(filt_db.Email[0])
            else:
                bv2 = filt_db.search_attr_exact_match('First_Name', firstname)
                if not bv2.any():
                    raise KeyError, "could not find a firstname match for %s, %s" % (lastname, firstname)
                elif bv2.sum() == 1:
                    filt2 = filt_db.filter(bv2)
                    return str(filt2.Email[0])
                else:
                    msg3 = "found more than one first name match for %s, %s"
                    raise KeyError, msg3 % (lastname, firstname)

            

## txt_database.db_from_file('LLL_grading_and_assessment.csv')
## mydb = txt_database.db_from_file('LLL_grading_and_assessment.csv')
## mydb.Last_Name
## mydb.First_Name
## email_list = txt_database.db_from_file('email_list.csv')
## email_list.Last_Name
## email_list.labels
