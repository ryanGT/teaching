import txt_mixin 
#import spreadsheet
from numpy import *
import rwkos, rwkmisc
import copy, os, re

item_pat = 'Item Analysis - Survey:'

def list_to_latex_row(row_list):
    return ' & '.join(row_list)+' \\\\'

def _latex_label_format(labels, fstr='\\textbf'):
    flist = [fstr+'{'+item+'}' for item in labels]
    label_str_out = ' & '.join(flist)+ ' \\\\'
    return label_str_out

def format_analysis_row(rowin):
    row_str = '%s & %i & %i & %0.2f & %0.2f \\\\' % rowin
    return row_str


summer_courses = ['452','454']

class csv_parser(txt_mixin.txt_file_with_list):
    def decode_semester(self):
        if self.sem_str[0].lower() == 'f':
            self.semester = 'Fall'
        else:
            if self.course_num in summer_courses:
                self.semester = 'Summer'
            else:
                self.semester = 'Spring'
        
    def regexp_pathin(self):
        folder, filename = os.path.split(self.pathin)
        pat = 'ME_*([0-9]+)_*([A-Za-z]+)_*([0-9]+)_*(.*)\\.csv'
        p = re.compile(pat)
        q = p.search(filename)
        if q:
            self.course_num = q.group(1)
            self.sem_str = q.group(2)
            self.year = int(q.group(3))
            if self.year < 100:
                self.year += 2000
            self.path_rest = q.group(4)
            self.decode_semester()
            
    def __init__(self, *args, **kwargs):
        txt_mixin.txt_file_with_list.__init__(self, *args, **kwargs)
        self.parse()
        self.regexp_pathin()

    def _build_pathout(self, ending):
        filename = 'ME%s_%s_%s_%s_nh.tex' % (self.course_num, \
                                            self.semester, \
                                            self.year, ending)
        pathout = os.path.join(self.folder, filename)
        return pathout
        
    def save_summary_latex(self, pathout=None):
        if pathout is None:
            pathout = self._build_pathout('stats')
        if not hasattr(self, 'summary_latex'):
            self.Build_Summary_Latex()
        txt_mixin.dump(pathout, self.summary_latex)

    def save_analysis_latex(self, pathout=None):
        if pathout is None:
            pathout = self._build_pathout('item_analysis')
        if not hasattr(self, 'analysis_latex'):
            self.Build_Analysis_Latex()
        txt_mixin.dump(pathout, self.analysis_latex)

    def parse(self):
        self.start_inds = self.findall(item_pat)
        self.end_inds = copy.copy(self.start_inds)
        self.end_inds.pop(0)
        self.end_inds.append(None)
        self.items = None
        for start, end in zip(self.start_inds, self.end_inds):
            chunk = self.list[start:end]
            cur_item = eval_item(chunk)
            if self.items is None:
                self.items = [cur_item]
            else:
                self.items.append(cur_item)
                
##     def _latex_one_row(self, ind, float_fmt='%0.2f'):
##         #data = self.stats_data
##         keys = ['mean', 'size', 'missing', 'variance', 'std_dev']
##         fmts = [float_fmt, '%i', '%i', float_fmt, float_fmt]
##         cur_list = [str(ind+1)+': '+item_titles[ind]]
##         for key, fmt in zip(keys, fmts):
##             cur_attr = getattr(data, key)
##             if cur_attr:
##                 cur_value = cur_attr[ind]
##                 cur_str = fmt % cur_value
##                 cur_list.append(cur_str)
##         return self._list_to_row(cur_list)


    def latex_table_start(self):
        return '\\begin{tabular}{p{2.75in}*{5}{r}}'
##         if self.variance:
##             return '\\begin{tabular}{p{2.75in}*{5}{r}}'
##         else:
##             return '\\begin{tabular}{p{2.75in}*{4}{r}}'
    

##     def _latex_label_format(self, labels, fstr='\\textbf'):
##         flist = [fstr+'{'+item+'}' for item in labels]
##         label_str_out = ' & '.join(flist)+ ' \\\\'
##         return label_str_out

    def _build_course_title(self):
        course_title = 'ME %s %s %s' % (self.course_num, \
                                        self.semester, \
                                        self.year)
        self.course_title = course_title
        return self.course_title

    def build_summary_title(self):
        self._build_course_title()
        title_str = '\\subsection*{Summarized Student Evaluations: %s}' % \
                    self.course_title
        return title_str

    def build_analysis_title(self):
        self._build_course_title()
        title_str = '\\subsection*{Detailed Student Evaluations: %s}' % \
                    self.course_title
        return title_str
    
    def Build_Summary_Latex(self, add_section=True):
        tex_list = []
        out = tex_list.append
        ext = tex_list.extend

        #ext(self.Fancy_Header())

        if add_section:
            out(self.build_summary_title())
        
        out('')
        out('\\flushleft')
        out('')
        for i, item in enumerate(self.items):
            if i == 0:
                out(self.latex_table_start())
                labels0 = ['','','Sample','Number','','Standard']
                labels1 = ['Question', 'Mean', 'Size', \
                           'Missing', 'Variance', \
                           'Deviation']
##                 if not self.variance:
##                     labels0.pop(4)
##                     labels1.pop(4)
                
                #labels = ['Question', 'Mean', 'Sample Size', \
                #          'Number Missing', 'Variance', \
                #          'Standard Deviation']
                flabels0 = _latex_label_format(labels0)
                flabels1 = _latex_label_format(labels1)
                out(flabels0)
                out(flabels1)
                out('\\hline')
            if i % 2 :
                out('\\rowcolor[gray]{0.9}')

            out(item.latex_summary_row())

##             if (i % 6) == 5:
##                 out('\\end{tabular}')
        out('\\end{tabular}')
        self.summary_latex = tex_list
        return self.summary_latex

    def Build_Analysis_Latex(self, add_section=True):
        tex_list = []
        out = tex_list.append
        ext = tex_list.extend

        if add_section:
            out(self.build_analysis_title())
        
        out('')
        out('\\flushleft')
        out('')

        for item in self.items:
            ext(item.latex_analysis_chunk())
            out('')
            out('')
            
        self.analysis_latex = tex_list
        return self.analysis_latex


def clean_csv_text(textin):
    textout = copy.copy(textin)
    clean_list = [',','"',' ','\t',"'"]
    while textout[-1] in clean_list:
        textout = textout[0:-1]
    while textout[0] in clean_list:
        textout = textout[1:]
    return textout

analysis_labels = ['Label','Value','Frequency',\
                   'Percent','Valid Percent']

class eval_item(object):
    def regexp_title(self):
        pat = 'Item Analysis - Survey: ([0-9]+): (.*)'
        p = re.compile(pat)
        q = p.search(self.title)
        self.number = int(q.group(1))
        clean_title = q.group(2)
        self.clean_title = clean_csv_text(clean_title)
        

    def __init__(self, listin=None):
        self.listin = listin
        if listin is not None:
            self.parse()

    def parse(self):
        mylist = rwkmisc.clean_list_regexp(self.listin)
        title = mylist.pop(0)
        self.title = clean_csv_text(title)
        missing_line = mylist.pop()
        assert missing_line.find('Total Missing') != -1, \
               'Did not find "Total Missing" in ' + missing_line
        missing_list = missing_line.split(',')
        self.missing = int(missing_list[-1])
        total_line = mylist.pop()
        assert total_line.find('Total Valid') != -1, \
               'Did not find" Total Valid" in ' + total_line
        total_list = total_line.split(',')
        self.total_valid = int(total_list[-1])
        self.total = self.total_valid + self.missing
        self.list = mylist
        first = 1
        for rowstr in mylist:
            row = rowstr.split(',')
            if first:
                first = 0
                labels = [row[0]]
                values = [int(row[1])]
                freqs = [int(row[2])]
            else:
                labels.append(row[0])
                values.append(int(row[1]))
                freqs.append(int(row[2]))
        self.labels = [item.replace('"','') for item in labels]
        self.values = values
        self.freqs = freqs
        assert sum(self.freqs) == self.total_valid, \
               'Self.total != sum(self.freqs)'
        self.build_data()
        self.calc_stats()
        self.calc_percents()
        self.regexp_title()
        
    def build_data(self):
        data_list = None
        for freq, val in zip(self.freqs, self.values):
            curlist = [val]*freq
            if data_list is None:
                data_list = curlist
            else:
                data_list.extend(curlist)
        self.data = array(data_list)

    def calc_stats(self):
        if any(self.freqs):
            self.var = self.data.var(ddof=1)
            self.mean = self.data.mean()
            self.std = self.data.std(ddof=1)
            self.max = self.data.max()
            self.min = self.data.min()
        else:
            self.var = 0.0
            self.mean = 0.0
            self.std = 0.0
            self.max = 0.0
            self.min = 0.0

    def calc_percents(self):
        freqs = array(self.freqs, dtype=float)
        N1 = self.total
        N2 = self.total_valid
        self.percents = 100*freqs/N1
        self.valid_percents = 100*freqs/N2

    def latex_summary_row(self, float_fmt='%0.2f'):
        #data = self.stats_data
        keys = ['mean', 'total', 'missing', 'var', 'std']
        fmts = [float_fmt, '%i', '%i', float_fmt, float_fmt]
        cur_list = [str(self.number)+': '+self.clean_title]
        for key, fmt in zip(keys, fmts):
            cur_value = getattr(self, key)
            cur_str = fmt % cur_value
            cur_list.append(cur_str)
        return list_to_latex_row(cur_list)
    
    def latex_analysis_chunk(self, float_fmt='%0.2f'):
        tex_list = []
        out = tex_list.append

        out('\\parbox{\\textwidth}{')
        out('\\textbf{\\large %s}' % self.title)
        out('')
        labels = analysis_labels
        n = len(labels)-1

        out('\\vspace{0.05in}')
        out('\\begin{tabular}{l*{%i}{r}}'%n)
        out('\\hline')

        out(_latex_label_format(labels))
        out('\\hline')

        i = 0

        biglist = zip(self.labels, self.values, self.freqs, \
                      self.percents, self.valid_percents)
        for row in biglist:
            row_str = format_analysis_row(row)
            out(row_str)
            i += 1
            if (i < 5) and (i % 2):
                out('\\rowcolor[gray]{0.9}')
            if i == 5:
                out('\\hline')
        valid_percent = (100.0*self.total_valid)/self.total
        valid_tup = ('Total Valid',self.total_valid, valid_percent, \
                     100.0)
        valid_row_str = '%s & & %i & %0.2f & %0.2f \\\\' % valid_tup
        out(valid_row_str)
        missing_percent = (100.0*self.missing)/self.total
        missing_tup = ('Total Missing',-1, self.missing, \
                       missing_percent)
        missing_row_str = '%s & %i & %i & %0.2f & \\\\' % missing_tup
        out(missing_row_str)
        total_tup = ('Total', self.total, 100.0)
        total_row_str = '%s & & %i & %0.2f & \\\\' % total_tup
        out(total_row_str)
        
        out('\\end{tabular}')
        out('}')#end parbox
        out('\\vspace{0.3in}')
        return tex_list

        
if __name__ == '__main__':
    folder = rwkos.FindFullPath('siue/tenure/student_evaluations')
    #filename = 'ME452_S09_item_analysis.csv'
    #filename = 'ME482_F08_item_analysis.csv'
    filename = 'ME484_Spring_2009_item_analysis.csv'
    fno, ext = os.path.splitext(filename)
    pathin = os.path.join(folder, filename)
    myparser = csv_parser(pathin)
    myparser.save_summary_latex()
    myparser.save_analysis_latex()
    
