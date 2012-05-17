from scipy import *
import numpy
import spreadsheet
reload(spreadsheet)
from spreadsheet import CSVSpreadSheet, GradeSpreadSheetMany, \
                        BlackBoardGBFile
import txt_mixin
import copy

from IPython.core.debugger import Pdb

class course_grade_compiler(CSVSpreadSheet):
    def retrieve_multiple_grades(self, csvpath, column_labels, \
                                 name_label=None):
        if name_label is None:
            name_label = self.name_label
        retrieved_sheet = GradeSpreadSheetMany(csvpath, \
                                               namelabel=name_label,
                                               valuelabels=column_labels)
        retrieved_sheet.ReadNamesandValues()
        return retrieved_sheet

    def retrieve_one_grade(self, csvpath, column_label, \
                           name_label=None):
        if name_label is None:
            name_label = self.name_label
        if type(column_label) == str:
            column_labels = [column_label]
        else:
            column_labels = column_label
        return self.retrieve_multiple_grades(csvpath, column_labels, \
                                             name_label=name_label)


    def retrieve_quiz_grades(self, csvpath, N_quiz, \
                             label_pat='Quiz %d', **kwargs):
        self.N_quiz = N_quiz
        quiz_labels = [label_pat % (i+1) for i in range(N_quiz)]
        self.quiz_sheet = self.retrieve_multiple_grades(csvpath, \
                                                        column_labels=quiz_labels, \
                                                        **kwargs)
        return self.quiz_sheet

    def drop_lowest_quiz_grade_and_average(self):
        if not hasattr(self, 'quiz_sheet'):
            print('You must call retrieve_quiz_grades before calling\n'+\
                  'drop_lowest_quiz_grade_and_average.')
            return
        qs = self.quiz_sheet
        qs.valuelabels.append('Quiz Average')
        nr, nc = qs.values.shape
        zero_col = zeros((nr,1))
        qs.values = numpy.append(qs.values, zero_col, -1)
        for n, row in enumerate(qs.values):
            all_quizzes = row[0:-1]
            imin = all_quizzes.argmin()
            top_quizzes = numpy.delete(all_quizzes, imin)
            q_ave = top_quizzes.mean()
            qs.values[n, -1] = q_ave

    def get_values_from_sheet(self, grade_sheet, valuelabel):
        """Retrieve one column from grade_sheet which is assumed to be
        a GradeSpreadSheetMany instance.  Use valuelabel to select the
        correct column."""
        ind = grade_sheet.valuelabels.index(valuelabel)
        col = grade_sheet.values[:,ind]
        return col

    def assign_lastnames(self, lastnames):
        self.lastnames = txt_mixin.txt_list(lastnames)

    def assign_attr_from_sheet(self, grade_sheet, valuelabel, \
                               attr, dtype=float):
        assert hasattr(self, 'lastnames'), \
               'You must assign self.lastnames before calling assign_attr_from_sheet'
        values = zeros(len(self.lastnames), dtype=dtype)
        col = self.get_values_from_sheet(grade_sheet, valuelabel)
        gs_names = grade_sheet.lastnames
        for lastname, value in zip(gs_names, col):
            inds = self.lastnames.findall(lastname, forcestart=1)
            assert len(inds)==1, 'Did not find exactly one match for ' + \
                   lastname +'.\n len(inds) = '+str(len(inds))
            ind = inds[0]
            values[ind] = value
        setattr(self, attr, values)
        return values

    def append_scores_to_BB_file(self, bb, destlabel, values, \
                                 splitnames=True):
        bb.AppendColFromList(self.lastnames, destlabel, values, \
                             splitnames=splitnames)


    def __init__(self, pathin=None, name_label='Student Name', **kwargs):
        CSVSpreadSheet.__init__(self, pathin=pathin, **kwargs)
        self.name_label = name_label


class course_grade_compiler_team(course_grade_compiler):
    def retrieve_multiple_grades(self, csvpath, column_labels, \
                                 name_label=None):
        if name_label is None:
            name_label = self.name_label
        retrieved_sheet = GradeSpreadSheetMany(csvpath, \
                                               namelabel=name_label,
                                               valuelabels=column_labels, \
                                               split_names=False)
        retrieved_sheet.ReadNamesandValues()
        return retrieved_sheet


    def retrieve_one_grade(self, csvpath, column_label, \
                           name_label=None):
        if name_label is None:
            name_label = self.name_label
        return course_grade_compiler.retrieve_one_grade(self, \
                                                        csvpath, \
                                                        column_label, \
                                                        name_label=name_label)

