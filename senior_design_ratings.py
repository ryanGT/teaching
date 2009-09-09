"""This module for now is primarily for use with assessment.  I need
to find the average score of each team member for each area and then
output them to a spreadsheet.  I will then pick certain areas to use
for assessment and certain average ratings for exceeding, meeting, or
not meeting the assessment expectations."""

import spreadsheet
reload(spreadsheet)
from spreadsheet import GradeSpreadSheetMany

from scipy import *

import txt_mixin

import glob, copy, os

from IPython.Debugger import Pdb

alternates1 = {'Matt':'Matthew', 'Brent':'Brenton', \
              'Zach':'Zachary', 'Pat':'Patrick', \
              'Kris':'Kristopher', 'Phil':'Philip', \
               'Jon':'Jonathan', 'Chris':'Christopher', \
               'Bob':'Robert', 'Jake':'Jacob', \
               'Coleman':'Colemon'}

alternates = dict(zip(alternates1.values(), alternates1.keys()))

def extract_col(list_of_lists, ind):
    col = [row[ind] for row in list_of_lists]
    return col

def clean_key(string_in):
    string_out = string_in.replace(' ','_')
    return string_out

class student_col(object):
    def __init__(self, col_of_strs, categories):
        for cat, string in zip(categories, col_of_strs):
            if string:
                val = float(string)
            else:
                val = None
            key = clean_key(cat)
            setattr(self, key, val)

class student(object):
    def __init__(self, name, rating_sheets):
        self.name = name
        self.categories = rating_sheets[0].categories
        self.keys = [clean_key(item) for item in self.categories]
        for key in self.keys:
            first = 1
            for rating in rating_sheets:
                cur_col = rating.ratings[self.name]
                curdata = getattr(cur_col, key)
                if curdata:
                    if first:
                        data = [curdata]
                        first = 0
                    else:
                        data.append(curdata)
            setattr(self, key, data)

    def ave(self):
        ave_list = []
        for key in self.keys:
            ave_name = key+'_ave'
            data = getattr(self, key)
            ave = mean(data)
            setattr(self, ave_name, ave)
            if ave_list:
                ave_list.append(ave)
            else:
                ave_list = [ave]
        self.ave_ratings = ave_list

class one_rating(object):
    def __init__(self, chunk):
        self.raw_chunk = copy.copy(chunk)
        self.parse()

    def parse(self):
        stop_ind = None
        for n, row in enumerate(self.raw_chunk):
            if row[0] == '':
                stop_ind = n
                break
        self.rows = copy.copy(self.raw_chunk[0:stop_ind])
        self.row0 = self.rows.pop(0)
        self.rater = self.row0[1]
        self.row1 = self.rows.pop(0)
        assert self.row1[0].lower() == 'team members', \
               "Did not find 'team members' in the second row of chunk:\n" + \
               str(self.raw_chunk)
        self.team_members = filter(None, self.row1[1:])
        self.categories = extract_col(self.rows, 0)
        self.keys = [clean_key(item) for item in self.categories]
        self.ratings = {}
        for n, name in enumerate(self.team_members):
            col = extract_col(self.rows, n+1)
            mycol = student_col(col, self.categories)
            self.ratings[name] = mycol
        
class ratings_sheet(spreadsheet.CSVSpreadSheet):
    def __init__(self, path):
        spreadsheet.CSVSpreadSheet.__init__(self, path)
        self.sniff()
        self.ReadData()
        self.members_ind = self.Search_Down_Col(0,'team members')
        assert self.members_ind > -1, 'Did not find "team members" in first column of '+path
        self.first_names = self.alldata[self.members_ind][1:]
        self.first_names = filter(None, self.first_names)
        self.ratio_ind = self.Search_Down_Col(0,'ratios')
        self.ratios = self.alldata[self.ratio_ind][1:]
        if not self.ratios[-1]:
            self.ratios.pop()
        if not self.first_names[-1]:
            self.first_names.pop()

    def parse(self):
        colA = txt_mixin.txt_list(self.get_col(0))
        inds = colA.findall('name', forcestart=1)
        inds.append(None)
        chunks = []
        ratings = []
        prevind = inds[0]
        for ind in inds[1:]:
            cur_chunk = self.alldata[prevind:ind]
            chunks.append(cur_chunk)
            rating = one_rating(cur_chunk)
            ratings.append(rating)
            prevind = ind
        self.ratings = ratings
        self.categories = ratings[0].categories
        self.keys = ratings[0].keys
        return ratings

    def build_students(self):
        members = self.ratings[0].team_members
        first = 1
        self.students = [student(name, self.ratings) for \
                         name in members]
        return self.students

    def _rank_team(self, team, alts=alternates1):
        cur_first_names = copy.copy(team.first_names)
        cur_match = 0
        for item in self.first_names:
            if item in cur_first_names:
                cur_match += 1
                cur_first_names.remove(item)
            else:
                if alts is not None:
                    if alts.has_key(item):
                        cur_alt = alts[item]
                        if cur_alt in cur_first_names:
                            cur_match += 1
                            cur_first_names.remove(cur_alt)
        return cur_match
        
    def get_last_names(self, teams, alts=alternates1):
        """Find the lastnames of the team members by matching a team
        that has the right first names."""
        rankings = [self._rank_team(team) for team in teams]
        ind = argmax(rankings)
        myteam = teams[ind]
        team_first = copy.copy(myteam.first_names)
        team_last = copy.copy(myteam.last_names)
        last_names = None
        last_dict = None
        for first in self.first_names:
            try:
                ind = team_first.index(first)
            except ValueError:
                if alts.has_key(first):
                    cur_alt = alts[first]
                ind = team_first.index(cur_alt)
            cur_last = team_last.pop(ind)
            cur_first = team_first.pop(ind)
            if last_names:
                last_names.append(cur_last)
                last_dict[first] = cur_last
            else:
                last_names = [cur_last]
                last_dict = {first:cur_last}
        self.last_names = last_names
        self.last_dict = last_dict
        
    def average_ratings(self):
        """This method will average the ratings for each student in
        each category as rated by each member of their team."""
        ave_ratings = {}
        rat0 = self.ratings[0]
        members = rat0.team_members
        keys = rat0.keys
        ave_keys = [key+'_ave' for key in keys]
        for student in self.students:
            student.ave()
            student_data = [getattr(student, key) for key in ave_keys]
            ave_ratings[student.name] = student_data
        self.ave_ratings = ave_ratings

class team(object):
    def __init__(self, rowin):
        self.teamnum = int(rowin.pop(0))
        last_names = rowin.pop(0)
        if type(last_names) == str:
            templist = last_names.split(',')
            temp2 = [item.strip() for item in templist]
            self.last_names = [item.capitalize() for item in temp2]
        else:
            self.last_names = last_names
        
    def get_first_names(self, bbsheet):
        self.first_names = [bbsheet.Firstname_from_Last(item) for item in self.last_names]


    def find_ratings_sheet(self, ratings_sheets, alts=None):
        matches = []
        left_overs = []
        for sheet in ratings_sheets:
            cur_match = 0
            cur_first_names = copy.copy(sheet.first_names)
            for item in self.first_names:
                if item in cur_first_names:
                    cur_match += 1
                    cur_first_names.remove(item)
                else:
                    if alts is not None:
                        if alts.has_key(item):
                            cur_alt = alts[item]
                            if cur_alt in cur_first_names:
                                cur_match += 1
                                cur_first_names.remove(cur_alt)
                                
            matches.append(cur_match)
            left_overs.append(cur_first_names)
        inds = range(len(ratings_sheets))
        self.filt_inds = [item for item in inds if matches[item] > 1]
        self.filt_ratings_sheets = []
        for ind in self.filt_inds:
            self.filt_ratings_sheets.append(ratings_sheets[ind])
        if len(self.filt_inds) == 1:
            self.ind = self.filt_inds[0]
            self.ratings_sheet = ratings_sheets[self.ind]
            if matches[self.ind] == len(self.first_names):
                print('perfect match')
            else:
                print('left_overs='+str(left_overs[self.ind]))
                print('self.first_names='+str(self.first_names))
        else:
            if len(self.first_names) == 1:
                print('one man team')
                self.ratings_sheet = None
            else:
                print('================')
                print('more than one likely match')
                print('self.first_names='+str(self.first_names))
                print('================')

    def has_student(self, lastname):
        searchnames = [item.replace(' ','') for item in self.last_names]
        if lastname in searchnames:
            return True
        else:
            return False
        

class ME482_team_grade_sheet(spreadsheet.CSVSpreadSheet):
    def __init__(self, path):
        spreadsheet.CSVSpreadSheet.__init__(self, path)
        self.labelrow = 0 
        self.ReadData()
        team_nums_str = [item for item in self.get_col(0) if item]
        self.team_nums = [int(item) for item in team_nums_str]
        self.team_members = self.get_col(1)
        self.GetLabelRow()
        self.alldata.pop()#delete mostly empty row with overall average in it

class Senior_Design_BBFile(spreadsheet.BlackBoardGBFile):
    def __init__(self, path):
        spreadsheet.BlackBoardGBFile.__init__(self, path)
        self.ParseNames()

    def Find_Teams(self, teamlist):
        self.teamnums = []
        self.teams = []
        for lastname in self.lastnames:
            lastname = lastname.capitalize()
            filt_teams = [item for item in teamlist if item.has_student(lastname)]
            if len(filt_teams) == 1:
                self.teams.append(filt_teams[0])
                self.teamnums.append(filt_teams[0].teamnum)
            else:
                print('===================')
                print('No match for '+lastname)
                print('===================')
                self.teams.append(None)
                self.teamnums.append(-1)


    def Find_Ratios(self):
        self.ratios = []
        for firstname, team in zip(self.firstnames, self.teams):
            firstname = firstname.capitalize()
            ratings_sheet = team.ratings_sheet
            if ratings_sheet is None:
                self.ratios.append(1.0)
            else:
                search_names = ratings_sheet.first_names
                mylist = txt_mixin.txt_list(search_names)
                inds = mylist.findall(firstname)
                if len(inds) == 0:
                    if alternates.has_key(firstname):
                        inds = mylist.findall(alternates[firstname])
                if len(inds) == 1:
                    ratio = float(ratings_sheet.ratios[inds[0]])
                    if ratio > 1.1:
                        ratio = 1.1
                    elif ratio < 0.8:
                        ratio = 0.8
                    self.ratios.append(ratio)
                else:
                    print('===================')
                    print('did not find match for '+firstname)
                    print('in '+str(mylist))
                    print('===================')
                    self.ratios.append(-1)

def build_teams(team_path, bbfile=None):
    mysheet = spreadsheet.SpreadsheetFromPath(team_path)
    mysheet.ReadData()
    mysheet.alldata.pop(0)
    teams = [team(row) for row in mysheet.alldata]
    if bbfile is not None:
        for cur_team in teams:
            cur_team.get_first_names(bbfile)
    return teams
    
def load_all(glob_pat):
    csv_list = glob.glob(glob_pat)
    csv_list = [item for item in csv_list if item.find('template')==-1]
    first = 1
    for csv_path in csv_list:
        cur_sheet = ratings_sheet(csv_path)
        if first:
            ratings_sheets = [cur_sheet]
            first = 0
        else:
            ratings_sheets.append(cur_sheet)
    return ratings_sheets

def dump_averages(names, data, labels, outpath):
    """Get the averages for each student and dump to file."""
    labels.insert(0, 'Names')
    data_out = column_stack([names, data])
    spreadsheet.WriteMatrixtoCSV(data_out, outpath, labels)

def main(glob_pat, outpath, teampath, bbpath):
    """Find all the csv ratings sheets for glob_pat, load them,
    extract the averages for each student and dump the results to
    outpath."""
    ratings_sheets = load_all(glob_pat)
    names = None
    ave_data = None
    mybb = Senior_Design_BBFile(bbpath)
    teams = build_teams(teampath, mybb)
    for sheet in ratings_sheets:
        sheet.parse()
        sheet.build_students()
        sheet.average_ratings()
        sheet.get_last_names(teams)
        for name, aves in sheet.ave_ratings.iteritems():
            lastname = sheet.last_dict[name]
            fullname = lastname +', '+name
            if not names:
                names = [fullname]
                ave_data = [aves]
            else:
                names.append(fullname)
                ave_data.append(aves)
    labels = ratings_sheets[0].categories
    dump_averages(names, ave_data, labels, outpath)
    return names, ave_data

def _assess(values, exceeds_value, meets_value):
    assessment = zeros(len(values))
    for n, value in enumerate(values):
        if value >= exceeds_value:
            cur_a = 5.0
        elif value >= meets_value:
            cur_a = 3.0
        else:
            cur_a = 1.0
        assessment[n] = cur_a
    return assessment

def summarize(assessment, label):
    print(label + ' Assessmement:')
    plabels = ['Average','Exceeds','Meets','Does Not Meet']
    print('\t'.join(plabels))
    num_exceeds = where(assessment==5, 1,0).sum()
    num_meets = where(assessment==3, 1,0).sum()
    num_does_not_meet = where(assessment==1, 1,0).sum()
    summary_data = [assessment.mean(), num_exceeds, num_meets, \
                     num_does_not_meet]
    summary_strs = [str(item) for item in summary_data]
    print('\t'.join(summary_strs))

def save_assessment(outpath, names, values, assessment, labels):
    data = column_stack([names, values, assessment])
    spreadsheet.WriteMatrixtoCSV(data, outpath, labels)
    
def assess_one_area(ratings_path, value_label, exceeds_value, \
                    meets_value, outpath, name_label='Names'):
    grade_sheet = spreadsheet.GradeSpreadSheet(ratings_path, \
                                               namelabel=name_label, \
                                               valuelabel=value_label)
    names, values = grade_sheet.ReadNamesandValues(parsefunc=float)
    assessment = _assess(values, exceeds_value, meets_value)
    summarize(assessment, value_label)
    ass_label = value_label + \
                ' assessment (>= %s exceeds, >= %s meets)' % \
                (exceeds_value, meets_value)
    labels = [name_label, value_label, ass_label]
    save_assessment(outpath, names, values, assessment, labels)
    return assessment
    
if __name__ == '__main__':
    #compile 482 ratings info
    path482 = '/home/ryan/siue/classes/482'
    ratings_path = os.path.join(path482, 'ratings')
    glob_pat = os.path.join(ratings_path, '*.csv')
    outpath = '/home/ryan/siue/classes/482/assessment/482_team_ratings.csv'
    teampath = os.path.join(path482, 'teams.csv')
    bbpath = os.path.join(path482, 'class_list.csv')
    names, data = main(glob_pat, outpath, teampath, bbpath)
    #assess participation and teamwork
    assess_path = os.path.join(path482, 'assessment')
    apath =  os.path.join(assess_path, '482_participation_assessment.csv')
    participation_assessment = assess_one_area(outpath, 'Participation', 4.45, 3.7, apath)
    twpath = os.path.join(assess_path, '482_teamwork_assessment.csv')
    tw_assessement = assess_one_area(outpath, 'Teamwork', 4.45, 3.7, apath)

    #compile 484 ratings info
    path484 = '/home/ryan/siue/classes/484'
    ratings_path_484 = os.path.join(path484, 'ratings')
    glob_pat_484 = os.path.join(ratings_path_484, '*.csv')
    outpath484 = os.path.join(assess_path, '484_team_ratings.csv')
    names484, data484 = main(glob_pat_484, outpath484, \
                             teampath, bbpath)
    #assess 484 contribution
    contrib_labels = ["Technical Contribution","Project Management"]
    contrib_sheet = GradeSpreadSheetMany(outpath484, \
                                         namelabel='Names', \
                                         valuelabels = contrib_labels)
    names_contrib, data_contrib = contrib_sheet.ReadNamesandValues()
    contrib = data_contrib.mean(axis=1)
    contrib_assess = _assess(contrib, 90, 80)
    summarize(contrib_assess, 'Contribution')
    data = column_stack([names_contrib, data_contrib, contrib, \
                         contrib_assess])
    labels = ['Names','Technical Contribution','Project Management',\
              'Combined Contribution (average of Tech and PM)',\
              'Contribution Assessment (>=90 exceeds, >=80 meets)']
    contrib_path = os.path.join(assess_path, \
                                '484_contribution_assessment.csv')
    spreadsheet.WriteMatrixtoCSV(data, contrib_path, labels)
