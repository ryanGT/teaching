import txt_mixin
import txt_database
import copy, os
import numpy as np


def load_bb_csv(filename_in, enc='latin-1'):
    myfile = open(filename_in,'r', encoding=enc)
    mylist = myfile.readlines()
    return mylist


def clean_one_string(str_in):
    elim_list = ['<span>','</span>','<p>','</p>','<br>']
    replace_dict = {'Ê':' ','&nbsp;':' '}#,'&quot;':'"'} adding quotes
                                         #messes up csv readers

    strout = str_in
    
    for e in elim_list:
        strout = strout.replace(e,'')

    for key, val in replace_dict.items():
        strout = strout.replace(key,val)

    return strout

    
def clean_bb_csv_list(listin):
    listout = copy.copy(listin)
    
    for i, row in enumerate(listout):
        strout = clean_one_string(row)
        listout[i] = strout

    return listout


def get_unique_answers(listin):
    listout = []
    for item in listin:
        if item not in listout:
            listout.append(item)

    return listout


class bb_survey_bad_download(txt_mixin.delimited_txt_file):
    """I created this class initially to fix a survey sent to me by a
    colleague while working on a paper regarding EGR 345/346.  This
    person had downloaded blackboard survey results in such a way that
    everything was in one column and each repondent had as many rows
    as there where questions.  After the number of rows for respondent
    1, it started over for respondent 2.

    For whatever reason, I am leaving this as the base class."""
    def __init__(self, *args, **kwargs):
        txt_mixin.delimited_txt_file.__init__(self, *args, **kwargs)
        self.data = self.break_list()

    def get_answers_to_one_question(self, qnum):
        label = 'Question ID %i' % qnum
        answers = []
        N = len(self.data)

        for i in range(1,N):
            curlabel = self.data[i][0]
            if curlabel == label:
                answers.append(self.data[i][2])

        return answers


    def get_answers(self):
        answers = {}

        for i in range(1,7):
            curanswers = self.get_answers_to_one_question(i)
            answers[i] = curanswers

        self.answers = answers


    def quantify_answers(self):
        numeric_answers = {}
        for i in range(2,7):
            txt_answers = self.answers[i]
            ans_dict = answer_dicts.nested_dict[i]
            inv_map = {v: k for k, v in ans_dict.items()}
            N = len(txt_answers)
            ans_array = np.zeros(N,dtype=float)

            for j, item in enumerate(txt_answers):
                nv = inv_map[item]
                ans_array[j] = nv

            numeric_answers[i] = ans_array

        self.numeric_answers = numeric_answers
        #self.numeric_answers = ans_num_list


    def calc_averages(self):
        averages = {}

        for i in range(2,7):
            cur_data = self.numeric_answers[i]
            ave = cur_data.mean()
            averages[i] = ave

        self.averages = averages


    def calc_one_hist(self, qnum):
        hist = {}
        cur_data = self.numeric_answers[qnum]

        for i in range(6):
            sum = 0
            for item in cur_data:
                if item == i:
                    sum += 1
            hist[i] = sum

        return hist

    def calc_histogram(self):
        hist = {}
        for i in range(2,7):
            cur_hist = self.calc_one_hist(i)
            hist[i] = cur_hist

        self.hist = hist

    def percent_hist(self):
        N = len(self.answers[3])

        phist = {}
        for i in range(2,7):
            cur_hist = self.hist[i]
            cur_p = {}
            for key, val in cur_hist.items():
                pval = val/N
                cur_p[key] = pval
            phist[i] = cur_p

        self.phist = phist



class bb_survey(bb_survey_bad_download):
    """This is probably the real base class that assumes the data is
    downloaded such that each respondent gets one row and each
    question is in its own column."""
    def __init__(self, filename):
        self.filename = filename
        listin = load_bb_csv(filename)

        fno, ext = os.path.splitext(filename)
        outname = fno + '_clean' + ext

        clean_list = clean_bb_csv_list(listin)
        txt_mixin.dump(outname, clean_list)
        
        self.db = txt_database.db_from_file(outname)

        
    def find_question_ids(self):
        row0 = self.db.data[0]

        ids = []
        N = len(row0)
        pat = 'Question ID'
        
        for i in range(N):
            curlabel = row0[i]
            if curlabel.find(pat) == 0:
                ids.append(curlabel)

        self.question_ids = ids
        self.nquestions = len(ids)
        return ids
    
        
    def get_answers(self):
        if not hasattr(self, 'nquestions'):
            self.find_question_ids()
            
        answers = {}
        for i in range(1,self.nquestions+1):
            attr = 'Answer_%i' % i
            ans = getattr(self.db, attr)
            answers[i] = ans.tolist()

        self.answers = answers


    def get_unique_answers_one_question(self, qnum):
        """Find the unique answers to a question.  This would mainly
        be helpful when getting ready to tabulate a Likert question"""
        return get_unique_answers(self.answers[qnum])


    def tabulate_likert(self, qnum, answers):
        """Answers is a list of possible Likert answers.  The list
        would need to be generated from either knowing the questions
        ahead of time by copying them from the survey or using the
        get_unique_answers_one_question method above.  Note that the
        get_unique_answers_one_question cannot possibly know how to
        sort the answers if you later want to assign numerica values
        to the answers.  The tabulated results will be in the same
        order as answers."""
        responses = self.answers[qnum]

        table_out = [None]*len(answers)
        
        for i, ans in enumerate(answers):
            cur_total = 0
            for resp in self.answers[qnum]:
                if resp == ans:
                    cur_total += 1
                    
            table_out[i] = cur_total

        return table_out


    def likert_to_latex_table(self, qnum, answers, hline=True):
        tabulated = self.tabulate_likert(qnum, answers)
        latexout = [r'Likert Option & Frequency \\']

        pat = r'%s & %s \\'
        
        for ans, freq in zip(answers, tabulated):
            curline = pat % (ans, freq)
            if hline:
                latexout.append(r'\hline')
            latexout.append(curline)

        return latexout


    def find_one_question(self, qnum):
        """Find 'Question ID N' in the first row of data.  The text
        for the question should be in the next spot"""
        row0 = self.db.data[0,:].tolist()
        label = 'Question ID %i' % qnum
        ind = row0.index(label)
        raw_question = row0[ind+1]
        clean_question = clean_one_string(raw_question)
        return clean_question
    

    def find_questions(self):
        questions = []

        for i in range(self.nquestions):
            qnum = i + 1
            curq = self.find_one_question(qnum)
            questions.append(curq)

        self.questions = questions
        return questions



    def build_csv_data(self):
        columns = []

        for i in range(self.nquestions):
            qnum = i + 1
            curq = self.questions[i]
            q_label = "Question %i: " % qnum
            q_out = q_label + curq
            curans = self.answers[qnum]
            curcol = [q_out] + curans
            columns.append(curcol)

        self.csv_data = np.column_stack(columns)
        return self.csv_data
        

    def save_csv(self, delim="\t"):
        if not hasattr(self, "csv_data"):
            self.build_csv_data()

        fno, ext = os.path.splitext(self.filename)
        outname = fno + '_clean_out.csv'

        txt_mixin.dump_delimited(outname, \
                                 self.csv_data, \
                                 delim=delim)
        
