import txt_mixin, os
from numpy import where, zeros, array, append, column_stack, row_stack

from spreadsheet_mapper import clean_quotes, delimited_grade_spreadsheet

#####################################################################
#
# The big need here is to be able to take a spreadsheet file that
# contains team grades and map them to an individual grade file,
# presumably downloaded from BlackBoard.  I think this requires three
# classes or spreadsheets, one that contains the team grades, one that
# specifies which team each student is on, and one that contains the
# individual student grades where we want to put the results.
#
# The final function would take a list of team grade columns and map
# them onto the individual grade spreadsheet using the student-to-team
# map/dictionary.
#
#####################################################################

class team_grade_dict(txt_mixin.delimited_txt_file):
    """This class creates a dictionary for one team grade."""
    def __init__(self, filepath, team_id_column_label, score_column, delim=','):
        self.filepath = filepath
        self.team_id_column_label = team_id_column_label
        self.score_column = score_column
        txt_mixin.delimited_txt_file.__init__(self, filepath, delim=delim)
        self._build_dict()


    def _build_dict(self):
        labels = self.array[0]
        id_ind = where(labels==self.team_id_column_label)[0][0]
        score_ind = where(labels==self.score_column)[0][0]

        mydict = {}
        
        for row in self.array[1:]:
            name = row[id_ind]
            score = row[score_ind]
            mydict[name] = score

        self.dict = mydict


class ind_mapper(delimited_grade_spreadsheet):
    """This class exists to map group grades to an individual
    spreadsheet-like file.  The spreadsheet-like input file must
    contain a column that uniquely identifies the team name.

    This was my first attempt and only works if the team id is in the
    same spreadsheet file where the output grades are desired."""
    def __init__(self, team_grade, ind_input_file_path, \
                 output_path, team_id_column_label='Team Number', \
                 delim=','):
        """team_grade is an instance of team_grade_dict"""
        self.ind_input_file_path = ind_input_file_path
        self.output_path = output_path
        self.team_id_column_label = team_id_column_label
        self.team_grade = team_grade
        txt_mixin.delimited_txt_file.__init__(self, ind_input_file_path, delim=delim)
        self._get_student_names()
        self.team_id_col = where(self.labels==self.team_id_column_label)[0][0]


    def map_grades(self):
        N = len(self.data[:,0])
        ind_grades = []

        for row in self.data:
            team = row[self.team_id_col]
            score = self.team_grade.dict[team]
            ind_grades.append(score)

        self.ind_grades = array(ind_grades)
        


    def save(self, delim=None):
        new_labels = append(self.labels, self.team_grade.score_column)
        new_data = column_stack([self.data, self.ind_grades])
        out_mat = row_stack([new_labels, new_data])
        txt_mixin.delimited_txt_file.save(self, pathout=self.output_path, \
                                          array=out_mat, \
                                          delim=delim)

        
class student_to_team_mapper(delimited_grade_spreadsheet):
    """This class exists to create a unique one-to-one mapping where
    each student's team can be determined.  This will server as a
    helper class for the new ind_grade_mapper_v2, where the
    spreadsheet input for that class does not have the teams in it.
    The input file for this class is assumed to have 'Last Name' in
    the first column and 'First Name' in the second column.
    last:first will be used to create (presumably) unique dictionary
    keys."""
    def __init__(self, path_in, team_id_column_label='Team Number', \
                 delim=','):
        #self.pathin = path_in
        txt_mixin.delimited_txt_file.__init__(self, path_in, delim=delim)
        self.labels = self.array[0]
        self.data = self.array[1:]
        self.team_id_column_label = team_id_column_label
        self.team_id_col = where(self.labels==self.team_id_column_label)[0][0]
        test_bool = self.labels[0:2] == ['Last Name','First Name']
        assert test_bool.all(), \
               "student_to_team_mapper file violates the name expectations of columns 0 and 1"
        self._get_student_names()
        self.teams = self.data[:,self.team_id_col]
        self._build_dict()


    def _build_dict(self):
        mydict = {}
        for last, first, team in zip(self.lastnames, self.firstnames, self.teams):
            key = last + ':' + first
            mydict[key] = team

        self.dict = mydict
        return self.dict


class multiple_team_grades(txt_mixin.delimited_txt_file):
    """This class creates a list of team_grade instances, one for each
    column label in score_columns."""
    def __init__(self, filepath, team_id_column_label, score_columns, delim=','):
        self.filepath = filepath
        self.team_id_column_label = team_id_column_label
        self.score_columns = score_columns
        self.delim = delim
        self.build_list()
        

    def build_list(self):
        mylist = []

        for score_column in self.score_columns:
            tgd = team_grade_dict(self.filepath, \
                                  self.team_id_column_label, \
                                  score_column, \
                                  delim=self.delim)
            mylist.append(tgd)
            
        self.list = mylist


class ind_grade_mapper_v2(delimited_grade_spreadsheet):
    """This class maps team grades to an individual grade sheet.  This
    class differs from the original ind_grade_mapper in two ways.
    First, the individual spreadsheet for this class is not required
    to have a column with each student's team, because that functionality
    is handled by student_to_team_mapper.  But a student_to_team_mapper
    must be passed in when creating an instace of this class.

    The other major difference between ind_grade_mapper_v2 and
    ind_grade_mapper is that in the v2 class, the team grades are from a
    multiple_team_grades class, which contains a list of team_grade_dict
    instances"""
    def __init__(self, ind_input_file_path, \
                 team_mapper, team_grades, \
                 output_path, delim=','):
        self.ind_input_file_path = ind_input_file_path
        self.output_path = output_path
        txt_mixin.delimited_txt_file.__init__(self, ind_input_file_path, delim=delim)
        self._get_student_names()
        self.team_mapper = team_mapper
        self.team_grades = team_grades

        
    def map_one_grade(self, team_grade):
        """Team grade is one element in self.team_grades.list"""
        N = len(self.lastnames)
        ind_grades = []

        for last, first in zip(self.lastnames, self.firstnames):
            key = last + ':' + first
            if last.lower().find('aastudent') > -1:
                score = '-1'
            else:
                team = self.team_mapper.dict[key]
                score = team_grade.dict[team]
            ind_grades.append(score)

        return array(ind_grades)


    def map_grades(self):
        new_labels = []
        new_grades = []

        for team_grade in self.team_grades.list:
            label = team_grade.score_column
            ind_grades = self.map_one_grade(team_grade)
            new_labels.append(label)
            new_grades.append(ind_grades)

        self.new_labels = new_labels
        self.new_grades = new_grades
        self.new_data = column_stack(new_grades)
        return new_labels, new_grades


    def append_grades(self):
        self.all_labels = append(self.labels, self.new_labels)
        self.all_data = column_stack([self.data, self.new_data])
        return self.all_labels, self.all_data

            
    def save(self, append=True, delim=None):
        if append:
            if not hasattr(self, 'all_labels'):
                self.append_grades()
            labels = self.all_labels
            data = self.all_data
        else:
            labels = self.new_labels
            data = self.new_data
        out_mat = row_stack([labels, data])
        txt_mixin.delimited_txt_file.save(self, pathout=self.output_path, \
                                          array=out_mat, \
                                          delim=delim)
