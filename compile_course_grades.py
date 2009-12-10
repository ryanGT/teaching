from scipy import *
import numpy
import spreadsheet
reload(spreadsheet)
from spreadsheet import CSVSpreadSheet, GradeSpreadSheetMany, \
                        BlackBoardGBFile

import copy

from IPython.Debugger import Pdb

class course_grade_compiler(CSVSpreadSheet):
    def retrieve_multiple_grades(self, csvpath, column_labels, \
                                 name_label='Student Name'):
        retrieved_sheet = GradeSpreadSheetMany(csvpath, \
                                               namelabel=name_label,
                                               valuelabels=column_labels)
        retrieved_sheet.ReadNamesandValues()
        return retrieved_sheet

    def retrieve_one_grade(self, csvpath, column_label, \
                           name_label='Student Name'):
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
        for n,row in enumerate(qs.values):
            all_quizzes = row[0:-1]
            imin = all_quizzes.argmin()
            top_quizzes = numpy.delete(all_quizzes, imin)
            q_ave = top_quizzes.mean()
            qs.values[n, -1] = q_ave
            
