import pytexutils, txt_mixin


def seperator_sheet(pathin, line1, line2='', line3='', \
                    headerpath='/home/ryan/siue/tenure/header.tex', \
                    runlatex=1):
    myline = '\\coverpage{%s}{%s}{%s}' % (line1, line2, line3)
    myfile = txt_mixin.txt_file_with_list(pathin=None)
    myfile.append_file_to_list(headerpath)
    myfile.list.append(myline)
    myfile.list.append('\\end{document}')
    myfile.writefile(pathin)
    if runlatex:
        return pytexutils.RunLatex(pathin)
