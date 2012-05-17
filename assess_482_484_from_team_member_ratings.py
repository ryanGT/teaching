from scipy import *
import numpy
import os
import spreadsheet
reload(spreadsheet)
import rwkos

import group_rst_parser
reload(group_rst_parser)


import copy

import spring_2012_484
course_module = spring_2012_484
#reload(spring_2012_484)

#import fall_2009_482

project_names = spring_2012_484.group_list.Project_Name
#project_names = fall_2009_482.group_list.Project_Name
## project_names = ['Motorized Hand Truck', \
##                  'Cougar Baja',
##                  'Solar Powered Refrigeration', \
##                  ]

from IPython.core.debugger import Pdb

def string_to_float(item):
    try:
        return float(item)
    except ValueError:
        return -1

def nested_list_to_floats(nested_list):
    list_out = None
    for row in nested_list:
        row_out = map(string_to_float, row)
        if list_out is None:
            list_out = [row_out]
        else:
            list_out.append(row_out)
    return list_out


def masked_mean(arrayin):
    if arrayin.min() < 0:
        m = numpy.ma.masked_array(arrayin, arrayin < 0)
        return m.mean()
    else:
        return arrayin.mean()

def col_ave(arrayin):
    nr, nc = arrayin.shape
    col_aves = zeros(nc)
    for n, col in enumerate(arrayin.T):
        cur_ave = masked_mean(col)
        col_aves[n] = cur_ave
    return col_aves.mean()


def clean_attr(attr_in):
    attr_out = attr_in.replace(' ','_')
    return attr_out

class student(spreadsheet.CSVSpreadSheet):
    def separate_labels_from_scores(self):
        nested_list = None
        for row in self.alldata:
            cur_scores = row[1:]
            if nested_list is None:
                nested_list = [cur_scores]
            else:
                nested_list.append(cur_scores)
        float_list = nested_list_to_floats(nested_list)
        self.scores = array(float_list, dtype=float)

    def find_col_ind(self, student=None, alt=None):
        if student is None:
            student = self
        if hasattr(student, 'firstname'):
            try:
                ind = self.names.index(student.firstname)
            except ValueError:
                ind = self.names.index(student.alt_first)
        else:
            try:
                ind = self.names.index(student)
            except ValueError:
                if alt is not None:
                    ind = self.names.index(alt)
                else:
                    raise
        return ind

    def find_col(self, student=None, alt=None):
        ind = self.find_col_ind(student=student, alt=alt)
        return self.scores[:,ind]

    def calc_self_mean(self):
        self.mean_self = masked_mean(self.scores_of_self)

    def find_self_rating(self):
        self.scores_of_self = self.find_col()
        self.calc_self_mean()

    def calc_team_factor(self):
        self.team_mean_of_me = col_ave(self.myscores)
        self.team_factor = self.team_mean_of_me/self.parent.overall_mean

    def calc_self_factor(self):
        self.self_factor = self.mean_self/self.mean

    def calc_mean(self):
        self.mean = col_ave(self.scores)

    def average_one_area(self, area):
        """Calculate the students average score in one area.  This
        will be used for assessment.  self.myscores is a matrix of
        everyones' scores of me.  The rows are different areas and the
        columns are teammates."""
        ind = self.areas.index(area)
        row = self.myscores[ind,:]
        curmean = row.mean()
        myattr = clean_attr(area) + '_ave'
        setattr(self, myattr, curmean)
        return curmean


    def assess_one_area(self, area, area_mean):
        myattr = clean_attr(area) + '_ave'
        myave = getattr(self, myattr)
        myfactor = myave/area_mean
        myattr = clean_attr(area) + '_factor'
        setattr(self, myattr, myfactor)
        return myfactor


    def __init__(self, firstname, lastname, alt_first=None, parent=None):
        self.csvname = firstname + '_' + lastname + '.csv'
        self.csvpath = os.path.join(folder, self.csvname)
        self.firstname = firstname
        self.lastname = lastname
        self.alt_first = alt_first
        if (not os.path.exists(self.csvpath)) and (alt_first is not None):
            if alt_first != firstname:
                self.csvname = alt_first + '_' + lastname + '.csv'
                self.csvpath = os.path.join(folder, self.csvname)

        if not os.path.exists(self.csvpath):
            if firstname.find(' ') > -1:
                first_no_mi, rest = firstname.split(' ',1)
                self.csvname = first_no_mi + '_' + lastname + '.csv'
                self.csvpath = os.path.join(folder, self.csvname)

        assert os.path.exists(self.csvpath), "Cannot find %s" % self.csvpath

        spreadsheet.CSVSpreadSheet.__init__(self, self.csvpath, \
                                             skiprows=4)
        self.ReadData()
        row1 = self.alldata.pop(0)
        self.names = row1[1:]
        self.names = [item.strip() for item in self.names]
        self.areas = self.get_col(0)
        self.separate_labels_from_scores()
        self.calc_mean()
        self.find_self_rating()
        self.calc_self_factor()
        self.parent = parent



class group(group_rst_parser.group_with_team_ratings):
    def __init__(self, group_name):
        group_rst_parser.group.__init__(self, group_name, \
                                        group_list=course_module.group_list, \
                                        email_list=course_module.email_list, \
                                        alts=course_module.alts)
        self.find_alt_firstnames()
        self.build_names_tuples()
        if len(self.names) == 1:
            return
        self.students = None
        for first, last, alt_first in zip(self.firstnames, self.lastnames, self.alt_firstnames):
            cur_student = student(first, last, alt_first=alt_first, parent=self)
            if self.students is None:
                self.students = [cur_student]
            else:
                self.students.append(cur_student)


    def average_one_area(self, area):
        N = len(self.students)
        myarray = zeros(N)
        for i, student in enumerate(self.students):
            cur_mean = student.average_one_area(area)
            myarray[i] = cur_mean
        area_mean = myarray.mean()
        myattr = clean_attr(area) + '_ave'
        setattr(self, myattr, area_mean)
        return area_mean


    def assess_one_area(self, area):
        """Calculate a student assessment factor for one area.  The
        factor will be the students average rating in the area divided
        by the overall team average for that area."""
        if not hasattr(self, area+'_ave'):
            self.average_one_area(area)
        myattr = clean_attr(area) + '_ave'
        area_mean = getattr(self, myattr)
        N = len(self.students)
        myarray = zeros(N)
        for i, student in enumerate(self.students):
            cur_factor = student.assess_one_area(area, area_mean)
            myarray[i] = cur_factor
        myattr = clean_attr(area) + '_factor'
        setattr(self, myattr, myarray)
        return myarray


    ## def fix_team_factors(self):
    ##     N = float(len(self.names))
    ##     mymin = self.team_factors.min()
    ##     mymax = self.team_factors.max()
    ##     total = self.team_factors.sum()
    ##     i_max = self.team_factors.argmax()
    ##     i_min = self.team_factors.argmin()
    ##     self.raw_team_factors = copy.copy(self.team_factors)

    ##     if (mymax > 1.1) and (mymin < 0.8):
    ##         mytotal = total - mymax - mymin
    ##         scale = (N-0.8-1.1)/mytotal
    ##         self.team_factors = scale*self.raw_team_factors
    ##         self.team_factors[i_max] = 1.1
    ##         self.team_factors[i_min] = 0.8
    ##     elif mymin < 0.8:
    ##         #the team factors should still average to 1.0, even if
    ##         #someone went below 0.8, so solve for x where
    ##         #   0.8 + x*(sum of the rest) = N
    ##         #
    ##         # 05/01/10 - I am not sure I subscribe to this theory
    ##         # anymore.  Should everyone else's grade go up because
    ##         # they are mad at one person?
    ##         mytotal = total - mymin
    ##         scale = (N-0.8)/mytotal
    ##         self.team_factors = scale*self.raw_team_factors
    ##         self.team_factors[i_min] = 0.8
    ##     elif mymax > 1.1:
    ##         mytotal = total - mymax
    ##         scale = (N-1.1)/mytotal
    ##         self.team_factors = scale*self.raw_team_factors
    ##         self.team_factors[i_max] = 1.1

    ##     for student, tf in zip(self.students, self.team_factors):
    ##         student.team_factor = tf



    ## def calc_overall_ave(self):
    ##     self.means = array([student.mean for student in self.students])
    ##     self.overall_mean = self.means.mean()


    ## def find_student(self, name):
    ##     for student in self.students:
    ##         if student.firstname == name:
    ##             return student

    ## def get_data_for_student(self, name):
    ##     student_scores = None
    ##     for student in self.students:
    ##         cur_scores = student.find_col(name)
    ##         if student_scores is None:
    ##             student_scores = [cur_scores]
    ##         else:
    ##             student_scores.append(cur_scores)
    ##     mystudent = self.find_student(name)
    ##     mystudent.myscores = array(student_scores).T
    ##     mystudent.calc_team_factor()

    ## def get_student_scores(self):
    ##     for first in self.firstnames:
    ##         self.get_data_for_student(first)

    ## def check_team_factor_average(self):
    ##     team_factors = None
    ##     for student in self.students:
    ##         tf = student.team_factor
    ##         if team_factors is None:
    ##             team_factors = [tf]
    ##         else:
    ##             team_factors.append(tf)
    ##     team_factors = array(team_factors)
    ##     self.team_factors = team_factors

    ## def check_team_factors_ave(self):
    ##     self.team_factor_ave = self.team_factors.mean()
    ##     if abs(1.0 - self.team_factor_ave) > 1e-7:
    ##         print('possible problem with self.team_factor_ave: ' + \
    ##               str(self.team_factor_ave))
    ##         Pdb().set_trace()
    ##     if self.team_factors.max() > 1.1:
    ##         print('max team factor problem: ' + \
    ##               str(self.team_factors))
    ##     if self.team_factors.min() < 0.8:
    ##         print('min team factor problem: ' + \
    ##               str(self.team_factors))

    ## def get_self_ratings(self):
    ##     self.self_factors = [student.self_factor for student in self.students]


if __name__ == '__main__':
    case = 2#1 = 482, 2 = 484
    if case == 1:
        areas = ['Attendance', \
                 'Participation']
        course_path = rwkos.FindFullPath('siue/classes/482/2011/')
        bb_in_name = 'bb_my_factor_and_white_paper_EC.csv'
        outname = 'assessment_from_482_team_member_ratings.csv'

        folder = rwkos.FindFullPath('siue/classes/482/2011/team_ratings/final_482_ratings/ind_csv')

    else:
        areas = ['Teamwork', \
                 'Technical Contribution', \
                 'Project Management', \
                 'Contribution of Ideas']
        course_path = rwkos.FindFullPath('siue/classes/484/2012/')
        bb_in_name = 'bb_download_my_factor.csv'
        outname = 'assessment_from_484_team_member_ratings.csv'

        folder = rwkos.FindFullPath('siue/classes/484/2012/team_member_ratings/ind_csv')

    outfolder = rwkos.FindFullPath('siue/classes/484/2012/')

        ## 'Accuracy',
        ## 'Dependability',
        ## 'Teamwork',
        ## 'Knowledge',
        ## 'Communication',
        ## 'Quantity of Work',
        ## 'Quality of Work',
        ## 'Overall Value to the Team']


    bb_in_path = os.path.join(course_path, bb_in_name)
    assessment_path = os.path.join(outfolder, 'assessment')
    outpath = os.path.join(assessment_path, outname)
    bb = spreadsheet.BlackBoardGBFile_v_8_0(bb_in_path)
    for area in areas:
        bb.labels.append(area)
    bb.labels.append('Team Factor')
    bb.labels.append('Raw Team Factor')
    for pname in project_names:
        cur_group = group(pname)
        if len(cur_group.names) > 1:
            cur_group.calc_overall_ave()
            cur_group.get_student_scores()
            cur_group.calc_team_factor_average()
            cur_group.copy_team_factors_to_raw()
            cur_group.fix_team_factors()
            cur_group.check_team_factors_ave()
            cur_group.get_self_ratings()
            for area in areas:
                myarray = cur_group.assess_one_area(area)
                bb.InsertColFromList_v2(cur_group.lastnames, cur_group.firstnames, \
                                        area, \
                                        myarray, \
                                        verbosity=1)
        else:
            cur_group.team_factors = [1.0]
            cur_group.raw_team_factors = [1.0]
            for area in areas:
                bb.InsertColFromList(cur_group.lastnames, area, \
                                     [1.0], splitnames=0, \
                                     verbosity=1)
        ## InsertColFromList_v2(self.lastnames, self.firstnames, \
        ##                             key, val_list, \
        ##                             verbosity=2)
        bb.InsertColFromList_v2(cur_group.lastnames, cur_group.firstnames, \
                                'Team Factor', \
                                cur_group.team_factors, verbosity=1)
        bb.InsertColFromList_v2(cur_group.lastnames, cur_group.firstnames, \
                                'Raw Team Factor', \
                                cur_group.raw_team_factors, \
                                verbosity=1)
    #bb.save('../bb_out_test.csv')
    #bb.save('../team_factors.csv')
    bb.save(outpath)
