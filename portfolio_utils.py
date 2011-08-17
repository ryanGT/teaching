import pytexutils, txt_mixin


def seperator_sheet(pathin, line1, line2='', line3='', \
                    headerpath='/home/ryan/siue/tenure/header.tex', \
                    runlatex=1, space2='1.5in'):
    myline = '\\coverpagevar{%s}{%s}{%s}{%s}' % (line1, line2, line3, space2)
    myfile = txt_mixin.txt_file_with_list(pathin=None)
    myfile.append_file_to_list(headerpath)
    myfile.list.append('\\begin{document}')
    myfile.list.append(myline)
    myfile.list.append('\\end{document}')
    myfile.writefile(pathin)
    if runlatex:
        return pytexutils.RunLatex(pathin)



def many_sep_sheets(tuplist, space2='1.5in'):
    for cur_tuple in tuplist:
        pathin = cur_tuple[0]+'.tex'
        seperator_sheet(pathin, *cur_tuple[1:], space2=space2)

