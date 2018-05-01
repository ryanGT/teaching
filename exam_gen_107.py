import txt_database, txt_mixin, copy, re

from IPython.core.debugger import Pdb

ans_list = ['a','b','c','d','e','f']

class mc_problem(object):
    """A class for a multiple choice exam question"""
    def __init__(self, text, qnum, answers=[], points=3):
        """qnum is the question number that will be hard-coded into
        the markdown problem text."""
        self.text = text
        self.qnum = qnum
        self.answers = answers
        self.points = points


    def text_to_md(self):
        # use self.qnum rather than #
        outstr = '%i. (%i points) %s' % (self.qnum, self.points, self.text)
        return outstr
    

    def gen_md_list(self):
        line1 = self.text_to_md()
        out_list = [line1]

        for aletter, ans in zip(ans_list, self.answers):
            curline = '    %s. %s' % (aletter, ans)
            out_list.append(curline)

        return out_list


class true_or_false_problem(mc_problem):
    def __init__(self, text, qnum, answers=[], points=2):
        self.text = text
        self.qnum = qnum
        self.answers = answers
        self.points = points
    
    def text_to_md(self):
        outstr = '%i. (%i points) True or False:  %s' % \
                 (self.qnum, self.points, self.text)
        return outstr


    def gen_md_list(self):
        line1 = self.text_to_md()
        out_list = [line1]

        return out_list


class fill_in_the_blank(true_or_false_problem):
    def text_to_md(self):
        outstr = '%i. (%i points) %s' % \
                 (self.qnum, self.points, self.text)
        return outstr


class short_answer(fill_in_the_blank):
    """The main difference between a fill_in_the_blank question and
    a short answer question is the space that follows.  Neither has
    answers like an MC question.  Neither needs something added to
    the question statement like True or False.

    I am using two different classes for SA and FIB to allow for different
    spaces following the questions"""
    pass
    

class problem_from_path(mc_problem):
    def load_md(self):
        myfile = txt_mixin.txt_file_with_list(self.path)
        self.list = myfile.list

        
    def replace_qnum_and_points(self):
        replist = [('QNUM', str(self.qnum)), \
                   ('POINTS', str(self.points)), \
                   ]

        for i, row in enumerate(self.list):
            rowout = row
            for myfind, myrep in replist:
                rowout = rowout.replace(myfind, myrep)

            self.list[i] = rowout
                
        
    def __init__(self, text, qnum, answers=[], points=2):
        self.path = text
        self.qnum = qnum
        self.answers = answers
        self.points = points
        self.load_md()
        self.replace_qnum_and_points()


    def gen_md_list(self):
        return self.list


class pagebreak(object):
    def __init__(self):
        self.points = 0


    def gen_md_list(self):
        outlist = ['','\\pagebreak','']
        return outlist


class raw_md(object):
    def __init__(self, text):
        self.text = text
        self.points = 0

    def gen_md_list(self):
        outlist = [self.text]
        return outlist

    

question_class_dict = {'MC':mc_problem, \
                       'TF':true_or_false_problem, \
                       'path':problem_from_path, \
                       'FIB':fill_in_the_blank,
                       'SA':short_answer}


def get_answer_list(question):
    out_list = []
    
    for letter in ans_list:
        key = 'answer_%s' % letter
        attr = getattr(question, key)
        if attr:
            out_list.append(attr)

    return out_list
        

class exam_generator(txt_database.txt_database_from_file):
    def __init__(self, filepath=None, **kwargs):
        # potential problem for appending a parsed question:
        # there is no database to read and num_list can't
        # just be from a column of the db
        if filepath is None:
            self.num_list = None
        else:
            txt_database.txt_database_from_file.__init__(self, \
                                                         filepath=filepath, \
                                                         **kwargs)
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
        cur_q = qclass(qrow.text, self.next_qnum, answers, int(qrow.points))
        self.next_qnum += 1

        self.question_list.append(cur_q)


    def append_parsed(self, question):
        """Append a question that is coming from a parser and is already
        a question instance."""
        # - Do I want to do anything with num_from_file?
        # - Do I need to do something with self.num_list?
        question.qnum = self.next_qnum
        self.next_qnum += 1
        self.question_list.append(question)


    def append_list_from_parser(self, parser, inds=None):
        """I am assuming that the input inds are from question numbers
        that start at 1, while the list indices would start at 0."""
        if inds is None:
            #append all the questions
            for question in parser.questions:
                self.append_parsed(question)

        else:
            for ind in inds:
                self.append_parsed(parser.questions[ind-1])
            

    def append_pagebreak(self):
        self.question_list.append(pagebreak())


    def append_raw(self, text):
        raw_q = raw_md(text)
        self.question_list.append(raw_q)


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
            if type(question) is short_answer:
                out_list.append('\\saspace')
            else:
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


def parse_answers(qlist):
    """Extract a list of multiple choice answers from the question
    text list qlist, assuming that the answers are at the bottom of
    the list and start with optional whitespace followed by a single
    letter followed by a dot or parenthesis:

       a. this is one choice
       b) this is another choice
       c). might as well support both parenthesis and period
    """
    p = re.compile(r'^\s*[A-Za-z][.)]+ *(.*)')

    #print('='*10)
    #print('qlist at start of parse_answers: %s' % qlist)

    # clean the bottom of the incoming list

    while not qlist[-1]:
        qlist.pop(-1)

    ans_list = []

    # search up from the bottom of qlist
    N = len(qlist)
    
    for i in range(N):
        curline = qlist[-1]
        q = p.search(curline)
        if q:
            cur_ans = q.group(1)
            ans_list.append(cur_ans)
            qlist.pop(-1)
        else:
            break

    #print('qlist at end of parse_answers: %s' % qlist)
    
    ans_list.reverse()
    return ans_list



class md_question_parser(txt_mixin.txt_file_with_list):
    """This class parses a file that contains multiple, multi-line
    questions.  It reads in the file and chops it up into the
    individual questions.  It then parses each question and creates a
    list of question instances.

    Each question is assumed to start with a line like this, beginning
    with a #:

    # number, type, points

    or

    # 1, TF, 2 pts"""
    def break_list(self):
        """Break the raw list into a list of lists by assuming each
        question begins with a row that starts with a #"""
        inds = self.list.findallre('^#')
        self.nested_list = []

        for i in range(1, len(inds)):
            start_ind = inds[i-1]
            stop_ind = inds[i]
            curlist = copy.copy(self.list[start_ind:stop_ind])
            self.nested_list.append(curlist)

        # the last question goes from the last ind to the end of the
        # list
        last_list = copy.copy(self.list[inds[-1]:])
        self.nested_list.append(last_list)
        

    def parse_one_question(self, qlist):
        line1 = qlist.pop(0)
        info_list = line1.split(',')
        clean_info = [item.strip() for item in info_list]
        
        qnum, qtype, points = clean_info#assumes exactly 3 entries
        assert qnum[0] == '#', 'problem with qnum #'
        while qnum[0] == '#':
            qnum = qnum[1:]
        qnum = int(qnum)
        
        # if points includes numbers followed by spaces and/or
        # letters, clean the letters
        try:
            int_points = int(points)
        except:
            p = re.compile('^([0-9]+)')
            q = p.search(points)
            int_points = int(q.group(1))

        keys = [qtype, qtype.upper(), qtype.lower()]
        for key in keys:
            if key in question_class_dict:
                myclass = question_class_dict[key]
                break

        if qtype.upper() == 'MC':
            answers = parse_answers(qlist)
        else:
            answers = []


        # clean blank lines from the start
        while not qlist[0]:
            qlist.pop(0)

        text = '\n'.join(qlist)

        # I am not handling answers yet
        myquestion = myclass(text, None, answers=answers, points=int_points)
        myquestion.num_from_file = qnum#<-- not sure if this is a good idea
        return myquestion


    def parse_questions(self):
        self.questions = []
        
        for chunk in self.nested_list:
            #print('chunk: %s' % chunk)
            cur_question = self.parse_one_question(chunk)
            self.questions.append(cur_question)
            
    
    def __init__(self, filename):
        txt_mixin.txt_file_with_list.__init__(self, filename)
        self.break_list()
        self.parse_questions()
