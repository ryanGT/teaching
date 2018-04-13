import txt_database, txt_mixin

from IPython.core.debugger import Pdb

ans_list = ['a','b','c','d','e','f']

class mc_problem(object):
    """A class for a multiple choice exam question"""
    def __init__(self, text, answers=[], points=3):
        self.text = text
        self.answers = answers
        self.points = points


    def text_to_md(self):
        # use self.qnum rather than #
        outstr = '#. (%i points) %s' % (self.points, self.text)
        return outstr
    

    def gen_md_list(self):
        line1 = self.text_to_md()
        out_list = [line1]

        for aletter, ans in zip(ans_list, self.answers):
            curline = '    %s. %s' % (aletter, ans)
            out_list.append(curline)

        return out_list


class true_or_false_problem(mc_problem):
    def __init__(self, text, answers=[], points=2):
        self.text = text
        self.answers = answers
        self.points = points
    
    def text_to_md(self):
        outstr = '#. (%i points) True or False:  %s' % (self.points, self.text)
        return outstr


    def gen_md_list(self):
        line1 = self.text_to_md()
        out_list = [line1]

        return out_list


class problem_from_path(mc_problem):
    def load_md(self):
        myfile = txt_mixin.txt_file_with_list(self.path)
        self.list = myfile.list
        
    
    def __init__(self, text, answers=[], points=2):
        self.path = text
        self.answers = answers
        self.points = points
        self.load_md()
        

    def gen_md_list(self):
        return self.list


class pagebreak(object):
    def __init__(self):
        self.points = 0
    
    def gen_md_list(self):
        outlist = ['','\\pagebreak','']
        return outlist

    

question_class_dict = {'MC':mc_problem, \
                       'TF':true_or_false_problem, \
                       'path':problem_from_path}


def get_answer_list(question):
    out_list = []
    
    for letter in ans_list:
        key = 'answer_%s' % letter
        attr = getattr(question, key)
        if attr:
            out_list.append(attr)

    return out_list
        

class exam_generator(txt_database.txt_database_from_file):
    def __init__(self, *args, **kwargs):
        txt_database.txt_database_from_file.__init__(self, *args, **kwargs)
        self.num_list = self.number.astype(int).tolist()
        self.question_list = []
        self.next_qnum = 1
        

    def get_one_question(self, qnum):
        ind = self.num_list.index(qnum)
        qrow = self[ind]
        return qrow
    

    def append_one_question(self, qnum):
        qrow = self.get_one_question(qnum)
        qclass = question_class_dict[qrow.type]

        answers = get_answer_list(qrow)

        # pass in self.next_qnum here and then increment it
        cur_q = qclass(qrow.text, answers, int(qrow.points))

        self.question_list.append(cur_q)


    def append_pagebreak(self):
        self.question_list.append(pagebreak())
        

    def append_questions(self, qnumlist):
        """Append a list of questions by number"""
        for qnum in qnumlist:
            self.append_one_question(qnum)
            

    def gen_md(self, section_title=None):
        out_list = []

        if section_title:
            title_line = '# %s' % section_title
            out_list.append(title_line)
            out_list.append('')

        for question in self.question_list:
            cur_md = question.gen_md_list()
            out_list.extend(cur_md)
            out_list.append('\\mcspace')# note that spaces must be defined
                                        # in the main tex file
            out_list.append('')
            out_list.append('')

        self.md_list = out_list
        return self.md_list


    def save(self, filename):
        txt_mixin.dump(filename, self.md_list)


    def check_points(self):
        total = 0

        for question in self.question_list:
            total += question.points

        return total
