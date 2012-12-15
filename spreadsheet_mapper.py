import txt_mixin, os
from numpy import where, zeros, array, append, column_stack, row_stack
from delimited_file_utils import open_delimited_with_sniffer_and_check

import copy

#########################################################################
#
# I know I have several mostly working versions of this, but it is
# driving me crazy.  I often have multiple spreadsheets that I need to
# merge by mapping one or more columns from one sheet to the other
# while using one or more columsn as keys (lastname, firstname) for
# example.
#
# - How do I do this as intelligently as possible and make sure I can
# use it for 482/484 team grades as well?
#
# - I think this is relatively straight forward if I create a
# dictionary for the source spreadsheet and the two sheets agree on
# how the key is created.
#
#   --> using this approach, each spreadsheet-like class in this file
#       will need to have a make_keys_and_dict method
#
#       - each spreadsheet will have a self.rowdict property that maps
#       the keys to the row indices
#
#       - each source spreadsheet will have a self.valuesdict that
#       maps the keys to the values being read from the source sheet
#
#########################################################################

def clean_quotes(stringin):
    if stringin.startswith('"') and stringin.endswith('"'):
        stringout = stringin[1:-1]
    else:
        stringout = stringin
    return stringout


def strip(stringin):
    stringout = stringin.strip()
    return stringout


class delimited_grade_spreadsheet(txt_mixin.delimited_txt_file):
    """This class represents a delimited_txt_file where the first
    column contains student lastnames and the second column contains
    student first names.  The first row of this file contains column
    labels and the remaining rows contain the data."""
    def _set_name_cols(self):
        test_bool = self.labels[0:2] == ['Last Name','First Name']
        assert test_bool.all(), \
               "source_spreadsheet_first_and_lastnames file violates the name expectations of columns 0 and 1"
        self.lastnamecol = 0
        self.firstnamecol = 1

    
    def _get_labels_and_data(self):
        self.labels = self.array[0]
        self.data = self.array[1:]


    def clean_quotes(self,vect):
        vectout = map(clean_quotes, vect)
        return vectout


    def clean_firstnames(self):
        for i, fname in enumerate(self.firstnames):
            fname = fname.strip()
            if ' ' in fname:
                first, junk = fname.split(' ',1)
                fname = first
            self.firstnames[i] = fname.strip()
        return self.firstnames
    

    def _get_student_names(self):
        if not hasattr(self, 'data'):
            self._get_labels_and_data()

        if not hasattr(self, 'lastnamecol'):
            self._set_name_cols()

        self.lastnames = self.clean_quotes(self.data[:,self.lastnamecol])
        self.firstnames = self.clean_quotes(self.data[:,self.firstnamecol])


    def make_keys_and_dict(self):
        N = len(self.lastnames)
        keys = [None]*N
        i_vect = range(N)
        for i, first, last in zip(i_vect, self.firstnames, self.lastnames):
            key = '%s,%s' % (last, first)
            keys[i] = key
            
        self.keys = keys
        self.inds = i_vect
        self.rowdict = dict(zip(self.keys, self.inds))


    def map_from_source(self, source_sheet, label, attr=None, func=None):
        self.old_data = copy.copy(self.data)
        self.old_labels = copy.copy(self.labels)
        
        N = len(self.inds)
        mylist = [None]*N

        for key, ind in self.rowdict.iteritems():
            if source_sheet.valuesdict.has_key(key):
                value = source_sheet.valuesdict[key]
            else:
                #try only first initial
                last, first = key.split(',',1)
                alt_key = last + ',' + first[0:1] + '.'
                if source_sheet.valuesdict.has_key(alt_key):
                    value = source_sheet.valuesdict[alt_key]
                else:
                    raise KeyError, 'cannot find %s or %s in source_sheet.valuesdict' % (key, alt_key)
            if func is not None:
                value = func(value)
            mylist[ind] = value

        myarray = array(mylist)
        
        if attr is None:
            attr = label
            setattr(self, attr, myarray)

        new_labels = append(self.labels, label)
        new_data = column_stack([self.data, myarray])

        self.new_labels = new_labels
        self.new_data = new_data


    def replace_with_new(self):
        self.data = self.new_data
        self.labels = self.new_labels


    def save(self, output_path, delim=None):
        self.replace_with_new()
        out_mat = row_stack([self.labels, self.data])
        txt_mixin.delimited_txt_file.save(self, pathout=output_path, \
                                          array=out_mat, \
                                          delim=delim)


    def __init__(self, pathin=None, lastnamecol=0, firstnamecol=1, \
                 delim='\t', **kwargs):
        txt_mixin.delimited_txt_file.__init__(self, pathin, delim=delim, \
                                              **kwargs)
        myarray = open_delimited_with_sniffer_and_check(pathin)
        self.array = myarray
        self.lastnamecol = lastnamecol
        self.firstnamecol = firstnamecol
        self._get_labels_and_data()
        self._get_student_names()
        self.clean_firstnames()
        self.make_keys_and_dict()


class source_spreadsheet_first_and_lastnames(delimited_grade_spreadsheet):
    """This class exists to copy a column from one spreadsheet to
    another where both sheets contain information about individual
    students (i.e. not groups).  The keys for both sheets will be
    lastname,firstname."""
    def find_source_col(self):
        labels = self.labels.tolist()
        ind = labels.index(self.sourcecollabel)
        self.source_col_ind = ind


    def make_values_dict(self):
        values = self.data[:,self.source_col_ind]
        self.values = values
        self.valuesdict = dict(zip(self.keys, values))
        
        
    def __init__(self, pathin=None, sourcecollabel=None, \
                 lastnamecol=0, firstnamecol=1, \
                 delim='\t', **kwargs):
        delimited_grade_spreadsheet.__init__(self, pathin, \
                                             lastnamecol=lastnamecol, \
                                             firstnamecol=firstnamecol, \
                                             delim=delim, \
                                             **kwargs)
        self.sourcecollabel = sourcecollabel
        self.find_source_col()
        self.make_values_dict()



class group_delimited_grade_spreadsheet(delimited_grade_spreadsheet):
    """This is the group version of delimited_grade_spreadsheet where
    only the group name is needed and firstnames are irrelevant."""
    def _set_name_cols(self):
        test_bool = self.labels[0:1] == ['Group Name']
        assert test_bool.all(), \
               "source_spreadsheet_first_and_lastnames file violates the name expectations of column 0 for a group sheet"
        self.lastnamecol = 0
        self.firstnamecol = None



    def clean_firstnames(self):
        return None


    def _get_student_names(self):
        if not hasattr(self, 'data'):
            self._get_labels_and_data()

        if not hasattr(self, 'lastnamecol'):
            self._set_name_cols()

        self.lastnames = self.clean_quotes(self.data[:,self.lastnamecol])
        self.firstnames = None


    def make_keys_and_dict(self):
        N = len(self.lastnames)
        keys = [None]*N
        i_vect = range(N)
        for i, last in zip(i_vect, self.lastnames):
            key = last
            keys[i] = key

        self.keys = keys
        self.inds = i_vect
        self.rowdict = dict(zip(self.keys, self.inds))



class group_source_spreadsheet(group_delimited_grade_spreadsheet,\
                               source_spreadsheet_first_and_lastnames):
    """This class exists to copy a column from one spreadsheet to
    another where both sheets contain a column called 'Group Name'.
    The keys for both sheets will be lastname which is the Group Name."""
    def __init__(self, pathin=None, sourcecollabel=None, \
                 lastnamecol=0, firstnamecol=None, \
                 delim='\t', **kwargs):
        group_delimited_grade_spreadsheet.__init__(self, pathin, \
                                                   lastnamecol=lastnamecol, \
                                                   firstnamecol=firstnamecol, \
                                                   delim=delim, \
                                                   **kwargs)
        self.sourcecollabel = sourcecollabel
        self.find_source_col()
        self.make_values_dict()

