import pandas as pd
import txt_database

def open_clean_bb_csv_as_df(mypath):
    bbdb = txt_database.db_from_file(mypath)

    label0 = bbdb.labels[0].replace('\ufeff', '')

    label0 = label0.replace('"','')
    label0

    bbdb.labels[0] = label0
    bbdb.labels

    df = pd.DataFrame(data = bbdb.data, 
                      columns = bbdb.labels)
    return df

