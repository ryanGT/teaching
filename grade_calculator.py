import txt_database

from numpy import *

class grade_calculator(txt_database.txt_database):
    def try_all_to_float(self):
        for attr in self.attr_names:
            try:
                self.convert_cols_to_float(attr)
            except:
                print('could not convert attr to float: ' + attr)

    def __init__(self, pathin, cutoffs={'A':89.5,'B':79.5,'C':69.5,'D':59.5}):
        data, labels = txt_database._open_txt_file(pathin)
        txt_database.txt_database.__init__(self, data, labels)
        self.try_all_to_float()
        self.cutoffs= cutoffs

        
    def calc_grades(self):
        raise NotImplementedError


    def assign_letter_grades(self):
        N = len(self.grades_out)
        letter_grades = zeros(N, dtype='S1')
        gpa = zeros(N)
        for i, cur_grade in enumerate(self.grades_out):
            if cur_grade >= self.cutoffs['A']:
                letter_grades[i] = 'A'
                gpa[i] = 4.0
            elif cur_grade >= self.cutoffs['B']:
                letter_grades[i] = 'B'
                gpa[i] = 3.0
            elif cur_grade >= self.cutoffs['C']:
                letter_grades[i] = 'C'
                gpa[i] = 2.0
            elif cur_grade >= self.cutoffs['D']:
                letter_grades[i] = 'D'
                gpa[i] = 1.0
            else:
                letter_grades[i] = 'F'
                gpa[i] = 0.0
        self.letter_grades = letter_grades
        self.gpa = gpa


    def append_letter_grades(self, labels=['Letter Grade','GPA']):
        self.add_new_column(self.letter_grades, labels[0])
        self.add_new_column(self.gpa, labels[1])


    def append_grades(self, label='Course Grade'):
        self.add_new_column(self.grades_out, label)


    def run(self, pathout='grades_out_with_letter_grades.csv', \
            label='Course Grade', delim=','):
        self.calc_grades()
        self.append_grades(label=label)
        self.assign_letter_grades()
        self.append_letter_grades()
        self.save(pathout,delim=delim)
        
#My Factor,Team Factor,LLL Papers,Update Presentations,Email Updates,Update Meetings,Final Report,Final Presentation,Prototype Quality and Project Execution,Design,Analysis

class ME484_team_grade(grade_calculator):
    def calc_grades(self):
        team_part = 0.05*10*self.Update_Presentations + \
                    0.05*10*self.Email_Updates + \
                    0.05*10*self.Update_Meetings + \
                    0.2*self.Final_Report + \
                    0.2*self.Final_Presentation + \
                    0.2*self.Prototype_Quality_and_Project_Execution + \
                    0.1*self.Design + \
                    0.1*self.Analysis
        self.grades_out = team_part/0.95


    def append_grades(self, label='Team Grade'):
        grade_calculator.append_grades(self, label=label)


    def run(self, pathout='team_grades_out_with_letter_grades.csv', \
            label='Team Grade'):
        grade_calculator.run(self, pathout, label=label)
        
            
class ME484(grade_calculator):
    def calc_grades(self):
        team_part = 0.05*10*self.Update_Presentations + \
                    0.05*10*self.Email_Updates + \
                    0.05*10*self.Update_Meetings + \
                    0.2*self.Final_Report + \
                    0.2*self.Final_Presentation + \
                    0.2*self.Prototype_Quality_and_Project_Execution + \
                    0.1*self.Design + \
                    0.1*self.Analysis
        grades_out = 0.05*self.LLL_Papers + self.My_Factor*self.Team_Factor*team_part
        self.grades_out = grades_out
        


