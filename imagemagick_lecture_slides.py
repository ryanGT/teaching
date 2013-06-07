#!/usr/bin/env python
import os, txt_mixin
home_dir = os.path.expanduser('~')
path1 = os.path.join(home_dir, 'git')
teaching_path = os.path.join(path1, 'teaching')
header_path = os.path.join(teaching_path, 'imagemagick_background_header.tex')

class lecture_background(object):
    def __init__(self, course_str, date_stamp, lecture_path, num_slides=30):
        self.list = []
        self.date_stamp = date_stamp
        self.course_str = course_str
        self.stamp = course_str + '; ' + date_stamp
        self.lecture_path = lecture_path
        self.num_slides = num_slides
        

    def out(self, linein):
        self.list.append(linein)

        
    def preamble(self):
        self.out('\\input{%s}' % header_path)
        self.out('')
        self.out('\\hypersetup{')
        self.out('  pdfauthor={%s}' % self.stamp)
        self.out('}')
        self.out('')
        self.out('\\begin{document}')
        self.out('\\author[%s]{%s}' % (self.stamp, self.stamp))


    def append_one_frame(self, slide_num):
        self.out('\\begin{frame}[fragile]')
        self.out('')
        self.out('% dummy, slide_num=' + str(slide_num))
        self.out('')
        self.out('\\end{frame}')


    def build_filename(self):
        cn_str = self.course_str.replace(' ','_')
        date_str = self.date_stamp.replace('/','_')
        fn = '%s_%s_background.tex' % (cn_str, date_str)
        self.filename = fn

    def save(self):
        self.build_filename()
        exclude_dir = os.path.join(self.lecture_path, 'exclude')
        self.outpath = os.path.join(exclude_dir, self.filename)
        self.exclude_dir = exclude_dir
        txt_mixin.dump(self.outpath, self.list)

    def run_latex(self, pngs=True):
        curdir = os.getcwd()
        try:
            os.chdir(self.exclude_dir)
            latex_cmd = 'pdflatex ' + self.filename
            os.system(latex_cmd)
            if pngs:
                fno, ext = os.path.splitext(self.filename)
                self.pdf_name = fno + '.pdf'
                cmd = 'beamer_to_jpegs_or_pngs.py --png ' + self.pdf_name
                os.system(cmd)
        finally:
            os.chdir(curdir)
        
    def run(self):
        self.preamble()
        for i in range(self.num_slides):
            self.append_one_frame(i+1)

        self.out('')
        self.out('\\end{document}')
        self.save()
