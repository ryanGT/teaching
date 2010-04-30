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

def time_and_appearance_csv(overwrite=False):
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

if __name__ == '__main__':
    mysheet = time_and_appearance_csv()
    
