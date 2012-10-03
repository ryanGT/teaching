import txt_mixin, os
from numpy import where, zeros, array, append, column_stack, row_stack

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


class ind_mapper(txt_mixin.delimited_txt_file):
    """This class exists to map group grades to an individual
    spreadsheet-like file.  The spreadsheet-like input file must
    contain a column that uniquely identifies the team name."""
    def __init__(self, team_grade, ind_input_file_path, \
                 output_path, team_id_column_label='Team Number', \
                 delim=','):
        """team_grade is an instance of team_grade_dict"""
        self.ind_input_file_path = ind_input_file_path
        self.output_path = output_path
        self.team_id_column_label = team_id_column_label
        self.team_grade = team_grade
        txt_mixin.delimited_txt_file.__init__(self, ind_input_file_path, delim=delim)
        self.labels = self.array[0]
        self.data = self.array[1:]
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
