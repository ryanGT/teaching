import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

clean_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', \
                'C-', 'D+', 'D', 'F', 'W']
passing_grades = ['A','A-','B','B+','B-','C','C+']
c_plus_or_better = ['A','A-','B','B+','B-','C+']
grades_in_order = ['A','A-','B+','B','B-','C+','C','C-','D+','D','F','W']

def grades_in_list_bool(df, attr, grade_list):
    grades = df[attr]
    bool_array = grades.isin(grade_list)
    return bool_array


def passed_exact_attr_bool(df, attr):
    mybool = grades_in_list_bool(df, attr, passing_grades)
    return mybool


def failed_exact_attr_bool(df, attr):
    passed_bool = passed_exact_attr_bool(df, attr)
    failed_bool = ~passed_bool
    return failed_bool


def dfw_rate_for_attr(df, attr):
    failed_bool = failed_exact_attr_bool(df, attr)
    den = len(failed_bool)
    num = np.sum(failed_bool)
    return num/den*100


class pandas_registrar_df(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.read_excel(self.filepath)


    def clean_ex_grades(self, attr):
        list1 = ['C+','C','C-','D+','D','F']
        ex_grades = [item + ' EX' for item in list1]
        rep_dict = dict(zip(ex_grades, list1))
        self.df[attr].replace(rep_dict, inplace=True)


    def passed_class_bool(self, df, ):
        #for i in range(1,N+1):
        #    attr = "EGR %s %i" % (class_num, i)
        #    print(attr)
        #    cur_grades = df[attr]
        #    cur_pass = cur_grades.isin(passing_grades)
        #    if i == 1:
        #        passed = cur_pass
        #    else:
        #        passed += cur_pass
        passed = grades_in_list_bool(df, class_num, passing_grades, N=N)
        return passed


    def get_subpop(self, attr, value, df=None):
        if df is None:
            df = self.df
        mybool = df[attr] == value
        subpop = df[mybool]
        return subpop

    
    def get_subpop_list_of_values(self, attr, value_list):
        first = 1

        for value in value_list:
            curbool = self.df[attr] == value
            if first:
                mybool = curbool
            else:
                mybool += curbool

        subpop = self.df[mybool]
        return subpop



class pandas_egr_111(pandas_registrar_df):
    def clean_ex_grades(self):
        pandas_registrar_df.clean_ex_grades(self, attr=self.main_attr)


    def __init__(self, *args, **kwargs):
        pandas_registrar_df.__init__(self, *args, **kwargs)
        self.main_attr = "EGR 111 Grade"
        self.terms_in_order = ['Fall 2021','Winter 2022','Fall 2022','Winter 2023','Fall 2023']
        self.clean_ex_grades()

            

    def get_term_subpop(self, term, df=None):
        subpop = self.get_subpop("Term", term, df=df)
        return subpop


    def get_math_cohort(self, mth_list):
        if type(mth_list) == str:
            mth_list = [mth_list]
        subpop = self.get_subpop_list_of_values("Math Course", mth_list)
        return subpop


    def dfw_rate_over_time(self, subpop=None):
        if subpop is None:
            df = self.df
        else:
            df = subpop

        mylist = []
        for term in self.terms_in_order:
            term_subpop = self.get_term_subpop(term, df=subpop)
            term_dfw = dfw_rate_for_attr(term_subpop, self.main_attr)
            mylist.append(term_dfw)

        return mylist


    def plot_dfw_rate_over_time(self, ax, subpop=None, label=None, **kwargs):
        dfw_list = self.dfw_rate_over_time(subpop=subpop)
        N = len(self.terms_in_order)
        nvect = np.arange(N)
        ax.plot(nvect, dfw_list, label=label, **kwargs)
        ax.set_xticks(nvect, self.terms_in_order)
        ax.set_xlabel("Term")
        ax.set_ylabel("DFW Rate (%)")
        

    def get_letter_grade_total(self, subpop=None, grade="A"):
        if subpop is None:
            subpop = self.df
        letter_bool = subpop[self.main_attr] == grade
        N = np.sum(letter_bool) 
        return N


    def build_grade_hist(self, subpop=None):
        my_list = []
        for letter in grades_in_order:
            N = self.get_letter_grade_total(subpop=subpop, grade=letter)
            my_list.append(N)
        return my_list


    def plot_hist(self, ax, hist_list, label=None, **kwargs):
        N = len(grades_in_order)
        nvect = np.arange(N)
        ax.bar(nvect,hist_list, label=label, **kwargs)
        ax.set_xticks(nvect, grades_in_order)
        ax.set_ylabel("Number of Students")
