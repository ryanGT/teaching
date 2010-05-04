from scipy import *

import glob, copy, os

import spreadsheet
reload(spreadsheet)

import spring_2010_484
import txt_mixin

group_names = spring_2010_484.all_groups
group_list = spring_2010_484.group_list
alts = spring_2010_484.group_list

csvpath = '/home/ryan/484_2010/final_presentations/'

from IPython.Debugger import Pdb

def blank_time_and_appearance_csv(overwrite=False):
    if not os.path.exists(csvpath):
        os.mkdir(csvpath)
    myname = 'time_and_appearance.csv'
    pathout = os.path.join(csvpath, myname)

    mysheet = spreadsheet.TrueCSVSpreadSheet()
    mysheet.collabels = []
    mysheet.AppendCol('Team Name', group_names)
    empty_col = [None]*len(group_names)
    other_list = ['Appearance','Time']
    for col in other_list:
        mysheet.AppendCol(col, empty_col)
    mysheet.WriteDataCSV(pathout)
    return mysheet

time_app_name = 'time_and_appearance.csv'
time_app_path = os.path.join(csvpath, time_app_name)

judges_folder = '/home/ryan/484_2010/final_presentations/judges_ratings'
judges_filename = 'compiled_presentation_scores.csv'
judges_path = os.path.join(judges_folder, judges_filename)

################################
# Goal: output a csv file where each team has a final presentation
# score that includes appearance and a time penalty.
#~~~~~
# Plan:
# 1. read in judges ratings from judges_path
# 2. read in appearance and times from time_app_path
# 3. parse the time and calc penalty
# 4. compute final grade based on judges ave, appearance, and time
# 5. output final grade sheet
#~~~~~
# Note: the teams may not be in the same order in the different
# files.
################################


def get_timing_grade(time, max_t=11.0, min_t=9.0, grace=0.0):
    penalty = 0-.0
    if time > (max_t + grace):
        num_steps = int((time-max_t-grace)/0.5+0.95)
        penalty = -0.1*num_steps
    elif time < (min_t - grace):
        num_steps = int((min_t-grace-time)/0.5+0.95)
        penalty = -0.1*num_steps
    else:
        penalty = 0.0
    if abs(penalty) < 1e-4:
        #print('reseting penalty')
        penalty = 0.0
    return penalty


def parse_time_string(stringin):
    min_str, sec_str = stringin.split(':',1)
    time = float(min_str) + float(sec_str)/60.0
    return time


class big_sheet(spreadsheet.TrueCSVSpreadSheet):
    def __init__(self):
        col_map = {'Team Names':'team_name', \
                   'combined_ave':'judges_score'}

        judges_sheet = spreadsheet.TrueCSVSpreadSheet(judges_path, \
                                                      colmap=col_map)
        judges_sheet.FindLabelRow('Team Names')
        judges_sheet.FindDataColumns()
        judges_sheet.MapCols()
        self.judges_sheet = judges_sheet
        self.team_name = judges_sheet.team_name
        self.judges_score = judges_sheet.judges_score.astype(float)
        
        map2 = {'Team Name':'team_name', \
                'Appearance':'appearance', \
                'Time':'time'}
        time_app_sheet = spreadsheet.TrueCSVSpreadSheet(time_app_path, \
                                                        colmap=map2)
        time_app_sheet.FindLabelRow('Team Name')
        time_app_sheet.FindDataColumns()
        time_app_sheet.MapCols()
        self.time_app_sheet = time_app_sheet


    def retreive_time_and_app(self):
        N = len(self.team_name)
        app_grades = zeros(N)
        times = ['']*N
        time_penalty = zeros(N)
        other_team_list = txt_mixin.txt_list(self.time_app_sheet.team_name)
        
        for i, name in enumerate(self.team_name):
            ind = other_team_list.find(name)
            times[i] = self.time_app_sheet.time[ind]
            app_grades[i] = float(self.time_app_sheet.appearance[ind])

        self.time_strs = times
        self.times = [parse_time_string(item) for item in times]
        self.time_penalties = array([get_timing_grade(time) for time in self.times])
        self.appearance = app_grades


    def calc_pres_grades(self):
        self.pres_grades = 0.05*self.appearance + \
                           0.95*(self.judges_score + self.time_penalties)*10.0
        

    def save(self):
        outname = 'presentation_grades.csv'
        outpath = os.path.join(csvpath, outname)
        labels = ['Team Name', 'Time', 'Time Penalty', 'Appearance', \
                  'Judges Scores','Final Presentation Grade']
        mymap = {'Team Name':'team_name', \
                 'Time':'time_strs', \
                 'Time Penalty':'time_penalties', \
                 'Appearance':'appearance', \
                 'Judges Scores':'judges_score', \
                 'Final Presentation Grade':'pres_grades'}
        self.MapOut(outpath, mymap, labels=labels)


if __name__ == '__main__':
    #---------------
    #Generate blank time and appearance sheet
    #---------------
    #mysheet = blank_time_and_appearance_csv()
    bs = big_sheet()
    bs.retreive_time_and_app()
    bs.calc_pres_grades()
    bs.save()
