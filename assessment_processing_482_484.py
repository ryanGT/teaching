import numpy
from numpy import where
import spreadsheet
reload(spreadsheet)

import spring_2011_484
import txt_mixin

group_names = spring_2011_484.all_groups
group_list = spring_2011_484.group_list
alts = spring_2011_484.alts

import compile_course_grades as ccg
reload(ccg)
#import fall_2009_482
#base = fall_2009_482.group
import course_with_group
reload(course_with_group)
base = course_with_group.group

import os, txt_mixin, re
import rwkos

from spreadsheet import GradeSpreadSheetMany

from IPython.Debugger import Pdb

project_names = group_names


def clean_csv(pathin):
    fno, ext = os.path.splitext(pathin)
    clean_path = fno + '_clean' + ext
    myfile = txt_mixin.txt_file_with_list(pathin)

    N = len(myfile.list)
    i = 0

    pat = re.compile('.*[;"]$')
    
    while i < (N-1):
        line = myfile.list[i]
        q = pat.match(line)
        if q is None :
            #this line needs to be merged with the next one down
            cur_line = myfile.list.pop(i)#retrieves line and removes it from the list
            next_line = myfile.list[i]#retrieve without removing
            new_line = cur_line.rstrip() + ' ' + next_line.lstrip()
            myfile.list[i] = new_line
            N = len(myfile.list)
        else:
            i += 1
        


    myfile.replaceallre('(;"")+$','')
    myfile.replaceallre('^""$','')
    clean_list = filter(None, myfile.list)
    txt_mixin.dump(clean_path, clean_list)
    return clean_path, clean_list


def clean_by_number(i):
    raw_name_pat = 'rwk_assessment_482_484_2Item%i.csv'
    raw_name = raw_name_pat % i
    clean_path, clean_list = clean_csv(raw_name)
    return clean_path


def unquote(item):
    assert item[0] == '"', '%s does not start with "' % item
    assert item[-1] == '"', '%s does not end with "'% item
    return item[1:-1]


def break_row(string_in):
    """Take a row of quoted items that are semicolon delimited and
    break it into a list."""
    mylist = string_in.split('";"')
    first_item = mylist[0]
    assert first_item[0] == '"', "First item in list did not start with quote: " + str(string_in)
    first_item = first_item[1:]
    mylist[0] = first_item
    last_item = mylist[-1]
    assert last_item[-1] == '"', "Last item in list did not end with quote: " + str(string_in)
    last_item = last_item[0:-1]
    mylist[-1] = last_item
    return mylist


def splitnames(listin):
    lastnames = []
    firstnames = []
    for fullname in listin:
        last, first = fullname.split(',',1)
        last = last.strip()
        first = first.strip()
        if first.find(' ') > -1:
            first, middle = first.split(' ',1)
            first = first.strip()
        lastnames.append(last)
        firstnames.append(first)
    return lastnames, firstnames



def summary_row(ave, num_exceeds, num_meets, num_does_not):
    latex_out = ['\\subsection*{Summary}', \
                 '\\begin{tabular}{cccc}', \
                 'Average & Number of Students & Number of Students & Number of Students \\\\', \
                 'Score &  Exceeding Expectations & Meeting Expectations  & Not Meeting Expectations \\\\', \
                 '\\hline', \
                 ' %0.2f & %i & %i & %i \\\\' % (ave, num_exceeds, \
                                                 num_meets, num_does_not), \
                 '\\end{tabular}']
    return latex_out

    
class assessment_item(object):
    def __init__(self, item_number, header1, header2, source):
        self.item_number = item_number
        self.header1 = header1
        self.header2 = header2
        self.source = source


    def _find_header(self):
        self.row2 = break_row(self.header2)
        header = self.row2[0]
        p = re.compile('[0-9]+\\.(.*)')
        q = p.match(header)
        header2 = q.group(1)
        header2 = header2.strip()
        return header2


    def to_latex(self):
        latex_out = []
        out = latex_out.append
        header = self._find_header()
        first_line = '\\section*{Item \\#%i: %s}' % (self.item_number, header)
        out(first_line)
        out('')
        out('\\subsection*{Criteria:}')
        out('')
        out('\\begin{tabularx}{\linewidth}{XXX}')
        out('Exceeds Expectations & Meets Expectations & Does Not Meet Expectations \\\\')
        out('\\hline')
        out(self.row2[1])
        out('&')
        out(self.row2[2])
        out('&')
        out(self.row2[3])
        out('\\end{tabularx}')
        out('')
        out('\\subsection*{Source}')
        out(self.source)

        if hasattr(self, 'question'):
            out('\\subsection*{Question}')
            out(self.question)
            

        out('\\subsection*{Assessment}')
        table_lines = self.build_table(**kwargs)
        latex_out.extend(table_lines)

        return latex_out


class team_item(assessment_item):
    def __init__(self, item_number, header1, header2, source, \
                 team_names, number_of_members, scores):
        assessment_item.__init__(self, item_number, header1, header2, source)
        self.team_names = team_names
        self.number_of_members = number_of_members
        self.scores = scores

    def build_table(self, **kwargs):
        list_out = ['\\begin{tabular}{|l|c|c|}', \
                    '\\hline', \
                    'Group Name & \\# of members & Team Score \\\\', \
                    '\\hline', \
                    ]
        out = list_out.append
        N = len(self.team_names)
        ilist = range(N)
        for i, team, number, score in zip(ilist, self.team_names, \
                                          self.number_of_members, \
                                          self.scores):
            if (i % 2) == 0:
                out('\\rowcolor[gray]{0.9}')
            currow = team + ' & ' + str(number) + ' & ' + str(score) + ' \\\\'
            out(currow)
            out('\\hline')
        out('\\end{tabular}')
        return list_out




class individual_item(assessment_item):
    def __init__(self, item_number, header1, header2, source, \
                 lastnames, \
                 firstnames=None, scores=None):
        assessment_item.__init__(self, item_number, header1, header2, source)
        self.lastnames = lastnames
        self.firstnames = firstnames
        self.scores = scores


    def build_table(self, blanknames=True, breakrow=17, **kwargs):
        if hasattr(self, 'breakrow'):
            breakrow = self.breakrow
            
        start_row = '\\begin{tabular}{|l|l|c|}'
        label_row = 'Last Name & \\ First Name & Score \\\\'
        list_out = [start_row, \
                    '\\hline', \
                    label_row, \
                    '\\hline', \
                    ]
        out = list_out.append
        N = len(self.lastnames)
        ilist = range(N)
        for i, last, first, score in zip(ilist, self.lastnames, \
                                          self.firstnames, \
                                          self.scores):
            if (i % 2) == 0:
                out('\\rowcolor[gray]{0.9}')
            if blanknames:
                n = i+1
                student = 'Student \\#%i' % n
                data = (student, '', score)
            else:
                data = (last, first, score)
            currow = '%s & %s & %i \\\\' % data
            out(currow)
            out('\\hline')
            if i == breakrow:
                out('\\end{tabular}')
                out('')
                out(start_row)
                out('\\hline')
                out(label_row)
                out('\\hline')

        out('\\end{tabular}')
        return list_out


class survey_item(individual_item):
    def __init__(self, item_number, header1, header2, source, question, lastnames, \
                 firstnames=None, scores=None):
        individual_item.__init__(self, item_number, header1, header2, source, \
                                 lastnames, firstnames, scores)
        self.question = question
        
################################################################
#
# New, automated assessment stuff starting in May 2012
#
################################################################
class assessment_item_2012(object):
    def __init__(self, item_number, subtitle, source, \
                 exceeds_criteria, meets_criteria, does_not_meet_criteria):
        self.item_number = item_number
        self.subtitle = subtitle
        self.source = source
        self.exceeds_criteria = exceeds_criteria
        self.meets_criteria = meets_criteria
        self.does_not_meet_criteria = does_not_meet_criteria


    def to_latex(self, **kwargs):
        latex_out = []
        out = latex_out.append
        first_line = '\\section*{Item \\#%i: %s}' % (self.item_number, self.subtitle)
        out(first_line)
        out('')
        out('\\subsection*{Criteria:}')
        out('')
        out('\\begin{tabularx}{\linewidth}{XXX}')
        out('Exceeds Expectations & Meets Expectations & Does Not Meet Expectations \\\\')
        out('\\hline')
        out(self.exceeds_criteria)
        out('&')
        out(self.meets_criteria)
        out('&')
        out(self.does_not_meet_criteria)
        out('\\end{tabularx}')
        out('')
        out('\\subsection*{Source}')
        out(self.source)

        if hasattr(self, 'question'):
            out('\\subsection*{Question}')
            out(self.question)


        out('\\subsection*{Assessment}')
        table_lines = self.build_table(**kwargs)
        latex_out.extend(table_lines)

        return latex_out


    def calc_scores(self):
        self.scores = numpy.zeros(self.N, dtype=int)

        for i, raw_score in enumerate(self.raw_scores):
            if raw_score >= self.exceeds_cutoff:
                self.scores[i] = 5
            elif raw_score >= self.meets_cutoff:
                self.scores[i] = 3
            else:
                self.scores[i] = 1

        return self.scores


class team_item_2012(assessment_item_2012):
    def __init__(self, item_number, team_names, number_of_members, \
                 raw_scores, exceeds_cutoff, meets_cutoff, **kwargs):
        assessment_item_2012.__init__(self, item_number, **kwargs)
        self.team_names = team_names
        self.N = len(self.team_names)
        self.number_of_members = number_of_members
        self.raw_scores = raw_scores
        self.exceeds_cutoff = exceeds_cutoff
        self.meets_cutoff = meets_cutoff
        self.calc_scores()
                

    def build_table(self, **kwargs):
        list_out = ['\\begin{tabular}{|l|c|c|}', \
                    '\\hline', \
                    'Group Name & \\# of members & Team Score \\\\', \
                    '\\hline', \
                    ]
        out = list_out.append
        N = len(self.team_names)
        ilist = range(N)
        for i, team, number, score in zip(ilist, self.team_names, \
                                          self.number_of_members, \
                                          self.scores):
            if (i % 2) == 0:
                out('\\rowcolor[gray]{0.9}')
            currow = team + ' & ' + str(number) + ' & ' + str(score) + ' \\\\'
            out(currow)
            out('\\hline')
        out('\\end{tabular}')
        return list_out


class individual_item_2012(assessment_item_2012):
    def __init__(self, item_number, lastnames, \
                 raw_scores, exceeds_cutoff, meets_cutoff, \
                 firstnames=None, \
                 **kwargs):
        assessment_item_2012.__init__(self, item_number, **kwargs)
        self.lastnames = lastnames
        self.firstnames = firstnames
        self.N = len(self.lastnames)
        self.raw_scores = raw_scores
        self.exceeds_cutoff = exceeds_cutoff
        self.meets_cutoff = meets_cutoff
        self.calc_scores()


    def build_table(self, blanknames=True, breakrow=17, **kwargs):
        if hasattr(self, 'breakrow'):
            breakrow = self.breakrow

        start_row = '\\begin{tabular}{|l|l|c|}'
        label_row = 'Last Name & \\ First Name & Score \\\\'
        list_out = [start_row, \
                    '\\hline', \
                    label_row, \
                    '\\hline', \
                    ]
        out = list_out.append
        N = len(self.lastnames)
        ilist = range(N)
        for i, last, first, score in zip(ilist, self.lastnames, \
                                          self.firstnames, \
                                          self.scores):
            if (i % 2) == 0:
                out('\\rowcolor[gray]{0.9}')
            if blanknames:
                n = i+1
                student = 'Student \\#%i' % n
                data = (student, '', score)
            else:
                data = (last, first, score)
            currow = '%s & %s & %i \\\\' % data
            out(currow)
            out('\\hline')
            if i == breakrow:
                out('\\end{tabular}')
                out('')
                out(start_row)
                out('\\hline')
                out(label_row)
                out('\\hline')

        out('\\end{tabular}')
        return list_out


class survey_item_2012(individual_item_2012):
    def __init__(self, item_number, question, lastnames, \
                 raw_scores, exceeds_cutoff, meets_cutoff, \
                 firstnames=None, \
                 **kwargs):
        individual_item_2012.__init__(self, item_number, \
                                      lastnames=lastnames, \
                                      raw_scores=raw_scores, \
                                      exceeds_cutoff=exceeds_cutoff, \
                                      meets_cutoff=meets_cutoff, \
                                      firstnames=firstnames, \
                                      **kwargs)
        self.question = question


################################################################
#
# End 2012 stuff
#
################################################################

class item_parser(txt_mixin.txt_file_with_list):
    def __init__(self, clean_path, item_number):
        txt_mixin.txt_file_with_list.__init__(self, clean_path)
        self.clean_path = clean_path
        self.item_number = item_number
        self.type = None
        

    def delete_rows_with_empty_first_col(self):
        mypat = '^"";.*'
        empty_inds = self.list.findallre(mypat)
        while empty_inds:
            self.list.pop(empty_inds[0])
            empty_inds = self.list.findallre(mypat)


    def get_col(self, ind, remove_quote=True, func=None):
        mycol = []
        for row in self.list:
            row_list = row.split(';')
            item = row_list[ind]
            if remove_quote:
                item = unquote(item)
            if func is not None:
                item = func(item)
            mycol.append(item)
        return mycol
            

    def parse_data(self):
        """Parse the csv data (semicolon delimited) contained in
        self.list.

        1. Pull out the summary info in the first two rows

        2. Grab the Source (after intro, there should be a line that
        starts with Source;

        3. If the row immediately following Source; starts with
        Question:;, then this item contains survey results.  Store the
        Question.

        4. After Source; and the optional Question:;, there should be
        a line that starts with one of Team Name;, Group Name;, Last
        Name; or Student Name;

        5. Determine if this is an individual or team assessment.

        6. Read in the data."""
        
        self.header1 = self.list.pop(0)
        self.header2 = self.list.pop(0)
        self.delete_rows_with_empty_first_col()
        source_inds = self.list.findallre('^"Source";')
        assert len(source_inds) > 0, "Did not find a line that starts with Source;"
        assert len(source_inds) == 1, "Found more than one line starting with Source;"
        source_ind = source_inds[0]
        assert source_ind == 0, "Did not find Source; in first remaining row.  This is probably bad:" + \
               str(self.list)
        self.source_row = self.list.pop(source_inds[0])
        #source_row_list = self.source_row.split(';')
        #self.source = unquote(source_row_list[1])
        source_row_list = break_row(self.source_row)
        self.source = source_row_list[1]
        #Grab the question if this is a survey item
        q_inds = self.list.findallre('^"Question:*";')
        if q_inds:
            assert len(q_inds) == 1, "Found more than one line starting with Question;"
            q_ind = q_inds[0]
            q_row = self.list.pop(q_ind)
            q_row_list = break_row(q_row)
            #self.question = unquote(q_row_list[1])
            self.question = q_row_list[1]
            self.type = "survey"
        self.label_row = self.list.pop(0)

        self.labels = self.label_row.split(';')
        group_or_name_label = unquote(self.labels[0])
        assert group_or_name_label in ["Team Name", "Group Name", "Last Name", "Student Name"], "Invalid " + \
               "Group or Name label: " + group_or_name_label
        if group_or_name_label in ["Team Name", "Group Name"]:
            self.type = "team"
            team_names = self.get_col(0)
            number_ind = self.labels.index('"# of members"')
            number_of_members = self.get_col(number_ind, func=int)
            score_col = self.labels.index('"Team Score"')
            scores = self.get_col(score_col, func=int)
            myitem = team_item(self.item_number, self.header1, self.header2, self.source, \
                               team_names, number_of_members, scores)
        elif group_or_name_label in ["Last Name", "Student Name"]:
            lastnames = self.get_col(0)

            if '"First Name"' in self.labels:
                fn_col = self.labels.index('"First Name"')
                firstnames = self.get_col(fn_col)
            else:
                if lastnames[0].find(",") > -1:
                    lastnames, firstnames = splitnames(lastnames)
                else:
                    firstnames = None
            score_col = self.labels.index('"Assessment"')
            scores = self.get_col(score_col, func=int)
            
            if self.type == "survey":
                #item_number, header1, header2, source, question, lastnames
                myitem = survey_item(self.item_number, self.header1, self.header2, self.source, \
                                     self.question, \
                                     lastnames=lastnames, \
                                     firstnames=firstnames, scores=scores)
            else:
                self.type = "individual"
                myitem = individual_item(self.item_number, self.header1, self.header2, self.source, \
                                         lastnames=lastnames, \
                                         firstnames=firstnames, scores=scores)
        return myitem



class group(base):
    def __init__(self, group_name, group_list, item_number, score, alts=alts):
        base.__init__(self, group_name, group_list, alts=alts)
        self.item_number = item_number
        self.score = score

    def get_one_team_grade(self, collabel):
        attr = colmap[collabel]
        col = getattr(team_grade_sheet, attr)
        return float(col[self.ind])

    def get_grades(self):
        for label in out_labels:
            attr = colmap[label]
            val = self.get_one_team_grade(label)
            setattr(self, attr, val)

    def insert_grades_into_bb(self, bb):
        N = len(self.lastnames)
        val = self.score
        val_list = [val]*N
        key = 'Item %i' % self.item_number
        bb.InsertColFromList_v2(self.lastnames, self.firstnames, \
                                key, val_list, \
                                verbosity=2)


class BB_file_482_assessment(spreadsheet.BlackBoardGBFile_v_8_0):
    def insert_team_factor(self):
        self.AppendColFromList_v2(team_factors.lastnames, \
                                  team_factors.firstnames, \
                                  'Team Factor', \
                                  team_factors.team_factor)
        self.assign_col_to_attr('Team Factor', 'team_factor')


    
if __name__ == '__main__':
    latex_out = ['\\input{report_header}', \
                 '\\begin{document}', \
                 '\\flushleft']

    bb = BB_file_482_assessment('bb_assessment.csv')
    csvoutpath = 'assessment_482_484_2010_2011_ind_mapped.csv'
    items = range(1,23)
    #items = [1,2,3]
    #items = [4]
    labels = ['Item %i' % item for item in items]
    bb.labels.extend(labels)
    #'Zackrie', 'Quince', 'qzackri'
    ave_row = ['','','Average']
    exceeds_row = ['','','Exceeds']
    meets_row = ['','','Meets']
    does_not_row = ['','','Does Not Meet']
    total_row = ['','','Total']
    
    for i in items:
        clean_path = clean_by_number(i)

        #For each item, I need to get the data, determine if this is
        #an individual or team item, and then assign the assessment
        #scores to each individual student

        # Goal: one bb file with 22 columns containing individual
        # assessment scores for each student for each item

        cur_item = item_parser(clean_path, i)
        parsed_item = cur_item.parse_data()

        col_label = 'Item %i' % i
        
        if isinstance(parsed_item, team_item):
            for group_name, score in zip(parsed_item.team_names, parsed_item.scores):
               cur_group = group(group_name, group_list, \
                                 item_number=i, score=score, alts=alts) 
               cur_group.insert_grades_into_bb(bb)

        else:
            bb.InsertColFromList_v2(parsed_item.lastnames, parsed_item.firstnames, \
                                    col_label, parsed_item.scores, \
                                    verbosity=2)


        
        attr = 'item_%i' % i
        bb.assign_col_to_attr(col_label, attr)
        cur_data = getattr(bb, attr)
        ave = cur_data.mean()
        num_exceeds = len(where(cur_data==5)[0])
        num_meets = len(where(cur_data==3)[0])
        num_does_not = len(where(cur_data==1)[0])
        total = num_exceeds + num_meets + num_does_not
        
        ave_row.append(ave)
        exceeds_row.append(num_exceeds)
        meets_row.append(num_meets)
        does_not_row.append(num_does_not)
        total_row.append(total)

        if i > 0:
            latex_out.append('\\pagebreak')
            
        latex_out.extend(parsed_item.to_latex())
        latex_out.extend(summary_row(ave, num_exceeds, \
                                     num_meets, num_does_not))
        ## for pname in project_names[0:1]:
        ##     cur_group = group(pname, group_list, alts=alts)
        ##     cur_group.()
        ##     cur_group.insert_grades_into_bb(bb)
        #--------------------------------
##         bb.InsertColFromList(cur_group.lastnames, 'Team Factor', \
##                              cur_group.team_factors, splitnames=0, \
##                              verbosity=1)
    #bb.run('combined_grades_out.csv')
    new_rows = [ave_row, exceeds_row, meets_row, does_not_row, total_row]
    for item in new_rows:
        bb.alldata.append(item)

    latex_out.append('\\end{document}')
    texout = 'assessment_report_no_names.tex'
    txt_mixin.dump(texout, latex_out)
    #bb.save(csvoutpath)
