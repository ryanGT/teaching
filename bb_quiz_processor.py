import txt_database
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 14
import copy
from collections import Counter
import os, rwkos, glob, txt_mixin
import pylab_util as PU
import pdb

def string_cleaner(str_in):
    mytuples = [('&nbsp;','')]
    out_str = copy.copy(str_in)
    for pair in mytuples:
        out_str = out_str.replace(pair[0],pair[1])
    return out_str


def clean_string_list(mylist):
    list_out = [string_cleaner(item) for item in mylist]
    return list_out


class quiz_question(object):
    def __init__(self, qnum, parent):
        self.qnum = qnum
        self.parent = parent#parent must be a quiz_processor db


    def getpattr(self, attr):
        thing = getattr(self.parent, attr)
        return thing
    


    def find_correct_answer(self, tol=1e-4):
        """Search through auto_scores until the difference between an
        auto_score and self.possible_points is less than tol."""
        for i, auto in enumerate(self.auto_scores):
            if np.abs(auto-self.possible_points) < tol:
                self.correct_ans = self.clean_answers[i]
                return self.correct_ans


    def build_hist_dict(self):
        self.hist_dict = Counter(self.clean_answers)


    def get_answers_list(self):
        """When I plot, the x labels need to be ans 1, ans 2, ....
        This method takes the keys of self.hist_dict and puts them in
        a list"""
        ans_list = list(self.hist_dict.keys())
        ans_list.sort()
        self.ans_list = ans_list


    def get_hist_y_list(self):
        y_list = []
        for ans in self.ans_list:
            y = self.hist_dict[ans]
            y_list.append(y)
        self.bar_y_list = y_list


    def gen_hist(self, save=0):
        self.get_answers_list()
        self.get_hist_y_list()
        N = len(self.ans_list)
        x = np.arange(1,N+1)
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.bar(x,self.bar_y_list)
        self.ax.set_title("Question %i" % self.qnum)
        xlabels = ['Ans %i' % item for item in x]
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(xlabels)
        self.ax.set_ylabel('# of students')
        if save:
            rwkos.make_dir('figs')
            plt.tight_layout()
            fn = "question_%0.2i_hist.eps" % self.qnum
            fp = os.path.join('figs',fn)
            PU.mysave(fp)
            

    def gen_markdown(self):
        listout = []
        out = listout.append
        out("## Question %i: %s" % (self.qnum, self.question))
        #out('')
        #out("**Question:** %s" % self.question)
        out('')
        out('\\columnsbegin')
        out('\\column{0.4\\textwidth}')
        out("**Answers:**")
        out('')
        for i, ans in enumerate(self.ans_list):
            j = i+1
            if ans == self.correct_ans:
                line = '- **ans %i: %s**' % (j, ans)
            else:
                line = '- ans %i: %s' % (j, ans)
            out(line)
        out('')
        out('\\column{0.6\\textwidth}')
        out('')
        out('\\vspace{-0.25in}')
        out('\\myfig{0.95\\textwidth}{figs/question_%0.2i_hist.pdf}' % self.qnum)
        out('\\columnsend')
        out('')
        return listout


        
    def main(self, save=0):
        q_attr = "Question_%i" % self.qnum
        q_list = self.getpattr(q_attr)
        self.question = q_list[0]
        ans_attr = "Answer_%i" % self.qnum
        ans_list = self.getpattr(ans_attr)
        self.answers = ans_list
        self.clean_answers = clean_string_list(self.answers)
        # 'Possible_Points_1',
        # 'Auto_Score_1'
        possible_attr = 'Possible_Points_%i' % self.qnum
        possible_list = self.getpattr(possible_attr)
        self.possible_points = float(possible_list[0])
        auto_score_attr = 'Auto_Score_%i' % self.qnum
        auto_score_list = self.getpattr(auto_score_attr)
        pdb.set_trace()
        self.auto_scores = auto_score_list.astype(float)
        self.find_correct_answer()
        self.build_hist_dict()
        self.gen_hist(save=save)
        

class quiz_processor(txt_database.txt_database_from_file):
    def process_questions(self, save=0):
        questions = []
        for i in range(1,1000):
            q_attr = "Question_%i" % i
            if not hasattr(self, q_attr):
                break
            else:
                cur_q = quiz_question(i, self)
                cur_q.main(save=save)
                questions.append(cur_q)
        self.questions = questions


    def gen_markdown(self):
        big_list = []
        for q in self.questions:
            cur_md = q.gen_markdown()
            big_list.extend(cur_md)
        self.markdown = big_list


    def save_pres(self, title='"Quiz Results"'):
        cmd1 = "new_md_beamer_pres.py %s" % title
        os.system(cmd1)
        slides_files = glob.glob("*_slides.md")
        assert len(slides_files) == 1, "did not find exactly one match, found %i" % len(slides_files)
        md_fn = slides_files[0]
        txt_mixin.dump(md_fn, self.markdown)
        self.md_fn = md_fn
        

    def run_pandoc(self):
        cmd = "md_to_beamer_pres.py %s" % self.md_fn
        os.system(cmd)
        
