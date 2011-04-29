from scipy import *

import glob, copy, os

import spreadsheet
reload(spreadsheet)

import spring_2011_484
import txt_mixin

group_names = spring_2011_484.all_groups
group_list = spring_2011_484.group_list
alts = spring_2011_484.group_list

#csvpath = '/home/ryan/484_2010/final_presentations/judges_ratings'
csvpath = '/home/ryan/484_2011/final_presentation_score_sheets/judges_scores'

from IPython.Debugger import Pdb

def gen_judges_csv(overwrite=False):
    if not os.path.exists(csvpath):
        os.mkdir(csvpath)
    number_of_judges = 6

    categories = ['Problem Statement', \
                  'Speaking and Delievery', \
                  'Conclusions', \
                  'Slide Quality', \
                  'Prototype Quality']
    
    for team_name in group_names:
        listout = [team_name]
        judges_list = ['""'] + ['"Judge %i"' % (item + 1) \
                             for item in range(number_of_judges)]
        judges_row = ','.join(judges_list)
        listout.append(judges_row)
        for item in categories:
            listout.append("%s," % item)
        filename = team_name.replace(' ','_') + '.csv'
        pathout = os.path.join(csvpath, filename)
        if (not os.path.exists(pathout)) or overwrite:
            txt_mixin.dump(pathout, listout)

    return listout


class judges_ratings_sheet(spreadsheet.CSVSpreadSheet):
    def find_judge_row(self):
        for n, row in enumerate(self.alldata):
            if row[0] == '' and row[1] == 'Judge 1':
                return n
        return -1


    def get_col_list(self):
        self.collist = []
        for i in range(1, self.NJ+1):
            cur_col = self.get_col(i)
            col_data = cur_col[self.start_row:]
            self.collist.append(col_data)
            

    def get_judge_aves(self):
        self.ave_list = []
        for col in self.collist:
            filt_col = filter(None, col)
            float_col = map(float, filt_col)
            if any(float_col):
                self.ave_list.append(average(float_col))
        self.overall_ave = average(self.ave_list[1:])#ignore me for now
        self.krauss_ave = self.ave_list[0]
        self.combined_ave = 0.75*self.overall_ave + 0.25*self.krauss_ave
        

    def append_judge_aves(self):
        ave_row = ['Judges Averages'] + [str(item) for item \
                                         in self.ave_list]
        self.alldata.append(ave_row)


    def save(self):
        old_folder, filename = os.path.split(self.path)
        folder = os.path.join(csvpath, 'processed')
        if not os.path.exists(folder):
            os.mkdir(folder)
        outpath = os.path.join(folder, filename)
        print('outpath = ' + outpath)
        self.WriteAllDataCSV(outpath)


    def find_row(self, label):
        colA = self.get_col(0)
        try:
            ind = colA.index(label)
        except ValueError:
            ind = -1
        return ind
    

    def row_ave(self, label):
        ind = self.find_row(label)
        assert ind > -1, 'Did not find %s in column A.' % label
        row = self.alldata[ind][1:]
        filt_row = filter(None, row)
        float_row = map(float, filt_row)
        return average(float_row)


    def assess_speaking(self):
        self.clarity_and_eff = self.row_ave('Presentation: Clarity and Effectiveness')
        self.delivery = self.row_ave('Presentation: Speaking/Delivery')
        self.speaking_ave = 0.5*self.clarity_and_eff + \
                            0.5*self.delivery
        
        
    def __init__(self, team_name):
        filename = team_name.replace(' ','_') + '.csv'
        csv_in_path = os.path.join(csvpath, filename)
        spreadsheet.CSVSpreadSheet.__init__(self, csv_in_path)
        self.sniff()
        #Pdb().set_trace()
        self.ReadData(skiprows=1, minrows=3)
        self.jrow = self.find_judge_row()
        assert self.jrow > -1, 'Did not find the Judge row'
        self.start_row = self.jrow+1
        self.NJ = len(self.alldata[self.jrow]) - 1
        self.get_col_list()
        self.get_judge_aves()
        self.append_judge_aves()
        #self.assess_speaking()
        self.save()



class big_spreadsheet(spreadsheet.CSVSpreadSheet):
    def load_dress_scores(self):
        temp = spreadsheet.CSVSpreadSheet('dress_scores.csv')
        temp.FindLabelRow('Team Numbers')
        temp.FindDataColumns(['dress'])
        temp.ReadDataColumns()
        self.AppendCol('Dress', temp.data[:,0])


    def __init__(self, team_names, *args, **kwargs):
        spreadsheet.CSVSpreadSheet.__init__(self, *args, **kwargs)
        self.team_names = team_names
        #self.titles = [self.dictin[ind] for ind in self.inds]
        #self.AppendCol('Team Numbers', self.inds)
        self.collabels = []
        self.AppendCol('Team Names', self.team_names)


    def get_prop(self, propname):
        mylist = []
        for sheet in self.sheets:
            curval = getattr(sheet, propname)
            mylist.append(curval)
        setattr(self, propname, mylist)
        return mylist
    

    def append_props(self, proplist):
        for propname in proplist:
            curlist = self.get_prop(propname)
            self.AppendCol(propname, curlist)
            

    def process_sheets(self):
        self.sheets = []
        for team_name in self.team_names:
            cur_sheet = judges_ratings_sheet(team_name)
            self.sheets.append(cur_sheet)
            

    def save(self, pathout=None):
        if pathout is None:
            filename = 'compiled_presentation_scores.csv'
            pathout = os.path.join(csvpath, filename)
        self.WriteDataCSV(pathout)


if __name__ == '__main__':
    #~~~~~~~~~~~~~~~~~~~~~~~
    # make csv files to type in judges scores
    #~~~~~~~~~~~~~~~~~~~~~~~
    #listout = gen_judges_csv()

    #----------------------------------
    #
    #  Parse input from judges files
    #
    #----------------------------------
    ## monday_groups = ['Motorized Hand Truck', \
    ##                  'Beverage Launching Refrigerator', \
    ##                  'Green Refrigeration', \
    ##                  'Upright Wheelchair', \
    ##                  'Swirl Generator']

    ## wednesday_groups = ['Mechanized Tree Stand', \
    ##                     'Autonomous Vehicle', \
    ##                     'Simplified Water Purification',\
    ##                     'Cougar Baja', \
    ##                     'Green Pedaling', \
    ##                    ]
    
##     group_names = ['Autonomous Vehicle', \
##                    'Hydraulic Bicycle Transmission', \
##                   ]

##     for curname in group_names:
##         cursheet = judges_ratings_sheet(curname)

    big_sheet = big_spreadsheet(group_names)
    #big_sheet.load_dress_scores()
    big_sheet.process_sheets()
    big_sheet.append_props(['overall_ave', 'krauss_ave', \
                            'combined_ave', \
                            ])
    big_sheet.save()
