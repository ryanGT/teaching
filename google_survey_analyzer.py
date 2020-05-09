import txt_mixin
import txt_database
import copy, os
import numpy as np
import matplotlib.pyplot as plt

class question(object):
    def __init__(self, q_text, answers):
        self.q_text = q_text
        self.answers = answers


    def make_hist_dict(self):
        hist_dict = {}

        for ans in self.answers:
            if ans in hist_dict:
                hist_dict[ans] += 1
            else:
                hist_dict[ans] = 1

        self.hist_dict = hist_dict


    def get_bar_values(self, x_vals=range(1,6)):
        y_vals = []

        for i in x_vals:
            key = '%i' % i
            if key not in self.hist_dict:
                y_i = 0
            else:
                y_i = self.hist_dict[key]
            y_vals.append(y_i)

        self.bar_x = x_vals
        self.bar_y = y_vals


    def bar_chart(self, xlabels=None, figsize=(8,5),y_ticks=None, \
                  title=True):
        if xlabels is None:
            xlabels = ['Strongly\nDisagree','Disagree',\
                       'Neutral','Agree','Strongly\nAgree']
        if not hasattr(self, "bar_x"):
            self.get_bar_values()
        fig1 = plt.figure(figsize=figsize)
        ax1=fig1.add_subplot(111)
        ax1.bar(self.bar_x, self.bar_y)
        ax1.set_xticks(self.bar_x)
        print("setting xticklabels: %s" % xlabels)
        ax1.set_xticklabels(xlabels)
        ax1.set_ylabel("Number of Responses")
        if y_ticks is not None:
            ax1.set_yticks(y_ticks)
        if title:
            ax1.set_title(self.q_text)

        return ax1


    def save_chart(self, figname, dpi=300):
        plt.savefig(figname, dpi=dpi,bbox_inches='tight')


class google_survey_csv(txt_database.txt_database_from_file):
    def extract_questions(self):
        self.questions = []
        nr, nc = self.data.shape
        for i in range(1,nc):
            q_text = self.labels[i]
            ans_data = self.data[:,i]
            cur_q = question(q_text, ans_data)
            self.questions.append(cur_q)


    def build_hist_dicts(self):
        for q in self.questions:
            q.make_hist_dict()
