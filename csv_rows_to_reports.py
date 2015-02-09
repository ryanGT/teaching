import os
import rst_creator, txt_database, txt_mixin, rwkos

title_dec = rst_creator.rst_title_dec()

class csv_rows_to_reports_converter(object):
    """This class exists to make it easy to take a csv file and
    convert it to one report per row.  This could be used to give a
    student team a grade report based on a csv file."""
    def __init__(self, csvpathin, folderout='out', \
                 basename_pat='report_%0.2i.rst',
                 title_pat='My Title %i', \
                 ignorecols=[]):
        self.csvpathin = csvpathin
        self.folderout = folderout
        self.basename_pat = basename_pat
        self.title_pat = title_pat
        self.ignorecols = ignorecols
        self.db = txt_database.db_from_file(csvpathin)
        self.N = len(self.db.data)

        self.filt_labels = [item for item in self.db.labels if item not in ignorecols]



    def process_one_row(self, ind):
        group_num = ind + 1
        mytitle = self.title_pat % group_num
        listout = title_dec(mytitle)
        out = listout.append
        out('')
        out('.. include:: /Users/rkrauss/git/report_generation/header.rst')
        out('')
        out('`\\thispagestyle{empty}`')
        out('')
        out('')
        
        
        for label in self.filt_labels:
            attr = txt_database.label_to_attr_name(label)
            val = getattr(self.db, attr)[ind]
            out('`\\rule{0pt}{1.5EM}`')
            row = '%s: %s' % (label, val)
            out(row)
            out('')

        return listout


    def build_out_paths(self):
        out_paths = []
        for i in range(self.N):
            group_num = i+1
            curname = self.basename_pat % group_num
            curpath = os.path.join(self.folderout, curname)
            out_paths.append(curpath)

        self.out_paths = out_paths
        return self.out_paths


    def process_all_rows(self):
        self.build_out_paths()
        rwkos.make_dir(self.folderout)
        
        for i in range(self.N):
            curlist = self.process_one_row(i)
            outpath = self.out_paths[i]
            txt_mixin.dump(outpath, curlist)


    def rst_to_pdf_all(self, basecmd = 'rst2latex_rwk.py %s'):
        for outpath in self.out_paths:
            cmd = basecmd % outpath
            os.system(cmd)
            
