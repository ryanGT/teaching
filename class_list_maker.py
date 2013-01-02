import txt_mixin, os, misc_utils, txt_database
from numpy import column_stack, row_stack

def get_names_from_Banner_txt(filename):
    #this approach assumes labels are in the top row (1 row of labels
    #only) and that the column label for the student names is "Student Name"
    mydb = txt_database.db_from_file(filename)
    names = mydb.Student_Name
    return names


def get_banner_ids(filename):
    if type(filename) == list:
        filename = filename[0]
    #mysheet = spreadsheet.TabDelimSpreadSheet(filename)
    #mysheet.ReadData()
    #ids = mysheet.get_col(2)
    mydb = txt_database.db_from_file(filename)
    ids = mydb.ID
    if ids[0].lower() == 'id':
        ids.pop(0)
    return ids
    

def combined_names_from_all_sections(fnlist):
    all_names = []
    poplist = ['Student Name']
    
    for fn in fnlist:
        names = get_names_from_Banner_txt(fn)
 
        if names[0] in poplist:
            names.pop(0)
 
        all_names.extend(names)

    all_names.sort()

    return all_names


def split_names(name_list, drop_middle=True):
    first_names = []
    last_names = []
        
    for name in name_list:
        last, first = name.split(',', 1)
        last = last.strip()
        first = first.strip()
        if drop_middle:
            if first.find(' ') > -1:
                first, middle = first.split(' ',1)
                first = first.strip()
        last_names.append(last)
        first_names.append(first)

    return last_names, first_names


def list_to_table_row(listin):
    row_str = ' & '.join(listin)
    row_str += ' \\\\'
    return row_str


def _get_names(csvlist):
    if type(csvlist) == str:
        csvlist = [csvlist]
    all_names = combined_names_from_all_sections(csvlist)
    last_names, first_names = split_names(all_names)

    return last_names, first_names

    
def make_class_list(csvlist, extra_col_labels=None, \
                    fmt_str=None, vrule='\\rule{0pt}{14pt}', \
                    hrule=None, headerpath=None, outpath=None, \
                    course='', semester='', section='', \
                    students_per_page=20):

    last_names, first_names = _get_names(csvlist)
    
    labels = ['Last Name', 'First Name']
    if extra_col_labels is not None:
        labels.extend(extra_col_labels)


    if fmt_str is None:
        N = len(labels)
        fmt_str = '|l' * N + '|'


    if headerpath is None:
        if os.path.exists('header.tex'):
            headerpath = 'header.tex'
        else:
            headerpath = '/home/ryan/git/report_generation/class_list_header.tex'

    headerline = '\\input{%s}' % headerpath
    startline = '\\begin{tabular}{%s}' % fmt_str
    latex_out = [headerline]
    out = latex_out.append
    out('\\pagestyle{fancy}')
    ws = ' '*4
    out(ws + '\\lhead{%s}' % course)
    out(ws + '\\rhead{%s}' % semester)
    out(ws + '\\chead{%s}' % section)
    out(ws + '\\rfoot{\\thepage}')
    out(ws + '\\lfoot{Ryan Krauss}')
    out(ws + '\\cfoot{}')
    out('\\renewcommand{\headrulewidth}{0pt}')
    out('\\begin{document}')
    out(startline)
    out('\\hline')

    label_row = list_to_table_row(labels)

    
    out(label_row)
    out('\\hline')

    if extra_col_labels is None:
        Nec = 0
    else:
        Nec = len(extra_col_labels)

    Nstudents = len(last_names)
    ilist = range(Nstudents)
    
    for i, last, first in zip(ilist, last_names, first_names):
        if (i % 2) == 0:
            out('\\rowcolor[gray]{0.9}')
        curlist = [last, first]
        if hrule is None:
            eclist = ['']*Nec
        else:
            eclist = [hrule]*Nec
        curlist += eclist
        last = curlist[-1]
        last += ' ' + vrule
        curlist[-1] = last
        currow = list_to_table_row(curlist)
        out(currow)
        out('\\hline')

        if i == students_per_page:
            out('\\end{tabular}')
            out('')
            out(startline)
            out('\\hline')
            out(label_row)
            out('\\hline')
            
    out('\\end{tabular}')
    out('\\end{document}')
    
    if outpath is not None:
        txt_mixin.dump(outpath, latex_out)

    return latex_out


def dumpcsv(outpath, csvlist, ids=False, extra_col_labels=None):
    last_names, first_names = _get_names(csvlist)
    N = len(last_names)

    vector_list = [last_names, first_names]
    
    labels = ['Last Name', 'First Name']
    if ids:
        banner_ids = get_banner_ids(csvlist)
        vector_list.append(banner_ids)
        labels.append('ID')

    if extra_col_labels is not None:
        labels.extend(extra_col_labels)
        Nec = len(extra_col_labels)
        for i in range(Nec):
            cur_empty = ['']*N
            vector_list.append(cur_empty)

    data = column_stack(vector_list)
    data2 = row_stack([labels, data])
    txt_mixin.dump_delimited(outpath, data2, delim=',', fmt='%s')
    #spreadsheet.WriteMatrixtoCSV(data2, outpath)
    
        
