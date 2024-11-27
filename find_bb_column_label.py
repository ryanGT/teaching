#!/usr/bin/env python3
import pandas as pd
import glob, re

# find latest bb csv file
# - xls files are corrupt

def find_bb_column_label(csvpath, pat_str, debug=1):
    if debug:
        print("csvpath: %s" % csvpath)
        print("pat_str = %s" % pat_str)
    data_df = pd.read_csv(csvpath)
    pat = re.compile(pat_str)
    
    for i, label in enumerate(data_df.columns):
        #print("label = %s" % label)
        q = pat.search(label)
        if q is not None:
            if debug > 0:
                print("MATCH: %s" % label)
            return(label)
        else:
            if debug:
                print("not a match: %s" % label)



