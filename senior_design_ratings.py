import spreadsheet
reload(spreadsheet)

from scipy import *

import txt_mixin

import glob, copy

from IPython.Debugger import Pdb

#Ultimately, I need to output a spreadsheet of grades for each
#student, showing their team grades for each item, overall team grade,
#and individual grade.  The individual grade depends on the team
#factor that must be extracted from the team spreadsheet.

#The team spreadsheet must determine the names of its members from a
#list of first names contained within itself, a class list that maps
#first names to last names, and a list of last names on each team.


class ratings_sheet(spreadsheet.CSVSpreadSheet):
    def __init__(self, path):
        spreadsheet.CSVSpreadSheet.__init__(self, path)
        self.sniff()
        self.ReadData()
        self.members_ind = self.Search_Down_Col(0,'team members')
        assert self.members_ind > -1, 'Did not find "team members" in first column of '+path
        self.first_names = self.alldata[self.members_ind][1:]
        self.ratio_ind = self.Search_Down_Col(0,'ratios')
        self.ratios = self.alldata[self.ratio_ind][1:]
        if not self.ratios[-1]:
            self.ratios.pop()
        if not self.first_names[-1]:
            self.first_names.pop()
        


alternates1 = {'Matt':'Matthew', 'Brent':'Brenton', \
              'Zach':'Zachary', 'Pat':'Patrick', \
              'Kris':'Kristopher', 'Phil':'Philip', \
               'Jon':'Jonathan', 'Chris':'Christopher', \
               'Bob':'Robert', 'Jake':'Jacob', \
               'Coleman':'Colemon'}

alternates = dict(zip(alternates1.values(), alternates1.keys()))


if __name__ == '__main__':
    path482 = '/home/ryan/siue/classes/482'
    ratings_path = os.path.join(path482, 'ratings')
    glob_pat = os.path.join(ratings_path, '*.csv')
    csv_list = glob.glob(glob_pat)
    csv_list = [item for item in csv_list if item.find('template')==-1]
