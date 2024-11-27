import re, os, glob
from krauss_misc import rwkos, relpath
from find_bb_column_label import find_bb_column_label
#import pdb
import bb_pandas_utils

html_pdf_links_str = r"""<p>Open: <a href="https://drive.google.com/open?id=IDSTR" target="_blank">https://drive.google.com/open?id=IDSTR</a></p>
<p>Download: <a href="https://drive.google.com/uc?export=download&id=IDSTR" target="_blank">https://drive.google.com/uc?export=download&id=IDSTR</a></p>"""

download_only_str = r"""<p>Download: <a href="https://drive.google.com/uc?export=download&id=IDSTR" target="_blank">https://drive.google.com/uc?export=download&id=IDSTR</a></p>"""

open_only_str = r"""<p>Open: <a href="https://drive.google.com/open?id=IDSTR" target="_blank">https://drive.google.com/open?id=IDSTR</a></p>"""

open_link_only_str = r"""https://drive.google.com/open?id=IDSTR"""

pure_open_only_str = r"""<p><a href="https://drive.google.com/open?id=IDSTR" target="_blank">https://drive.google.com/open?id=IDSTR</a></p>"""

pure_link_str = r'<p><a href="MYPATH" target="_blank">MYPATH</a></p>'

## Two forms of gdrive links:
#https://drive.google.com/file/d/1zzY_zN6DJMCZtohuMc0lgB8gzxOE01u5/view?usp=sharing
#https://drive.google.com/open?id=1zzY_zN6DJMCZtohuMc0lgB8gzxOE01u5
#https://docs.google.com/presentation/d/1y4s2w0wuN_MBtho-84gKhbRnza-_04FqS6bNQI30mJg/edit?usp=sharing
#https://docs.google.com/presentation/d/1y4s2w0wuN_MBtho-84gKhbRnza-_04FqS6bNQI30mJg/edit?usp=sharing
#https://drive.google.com/drive/folders/1K1QvjItpjSvSh1Y9MlZY1fczrC94oO4C?usp=sharing
#https://docs.google.com/document/d/1HjKxcGE2ITonkNe9SFfcBUX6FhLYQBR4euhTESZe9Q4/edit?usp=sharing
#https://docs.google.com/spreadsheets/d/16entjTxdN6CB1l-sTAC02orYOAeJHpvk5Pf-Gw2pOak/edit?usp=sharing

chop_list = ["/view","/edit"]
assign_pat = "(.*)_([0-9]+)"
assign_p = re.compile(assign_pat)


folder_to_assignment_dict = {'LA':'learning activity', \
                             'HW':'homework', \
                             'Quiz':'quiz', \
                             'quiz':'quiz', \
                             'Exam':'exam', \
                             'Project':'project', \
                             }

label_regexp_base_pats_dict ={'LA':'LA[_ ]*', \
                              #'LA':'[Ll]earning.*[Aa]ctivity *', \
                             #'HW':'[Hh]omework *', \
                             'HW':'[HhWw]+ *', \
                             'Quiz':'[Qq]uiz *', \
                             'quiz':'[Qq]uiz *', \
                             'Exam':'[Ee]xam *', \
                             'Project':'[Pp]roject *', \
                             }

prev_student_fn = "prev_student.txt"

def find_files_for_username(username):
    pat = "*%s*" % username
    all_files = glob.glob(pat)
    return all_files


def find_notebooks_for_username(username):
    pat = "*%s*.ipynb" % username
    nb_files = glob.glob(pat)
    return nb_files



def clean_course_path(pathin):
    # assumption: the google drive root is Teaching/course_folder and 
    # the local path is just ~/course_folder
    # - the local path is a symlink to a folder under mydrive/Teaching 
    #   with the same name
    #bad_part1 = "/Users/kraussry/Library/CloudStorage/GoogleDrive-ryanwkrauss@gmail.com/My Drive/Teaching"
    bad_part1 = "/Users/kraussry/Library/CloudStorage/GoogleDrive-kraussry@mail.gvsu.edu/My Drive/Teaching/EGR_445_545/445_SS24/"
    bad_parts = [bad_part1]#room for more later
    good_root = "/Users/kraussry/445_545_SS24/"
    pathout = pathin
    for bad_search in bad_parts:
        pathout = pathout.replace(bad_search, good_root)

    return pathout


def open_files_for_student(all_files):
    app_dict = dict({'pdf':'okular', \
                 'jpg':'eog', \
                 'png':'eog'})

    jupyter_root = "http://localhost:8888/lab/tree/445_545_SS24/grading"
    #root_345 = rwkos.get_root("345")
    # Note: this probably fails if the path hasn't been cleaned 
    # properly
    grading_root = "/Users/kraussry/445_545_SS24/grading" 
    curdir = os.getcwd()
    curdir = clean_course_path(curdir)
    reldir = relpath.relpath(curdir, grading_root)
    print("reldir = %s" % reldir)
    jup_folder = os.path.join(jupyter_root, reldir)
    print("jup_folder = %s" % jup_folder)
    
    for curfile in all_files:
        ## need better handling for chromebook and ipynb
        rest, ext = os.path.splitext(curfile)
        ext = ext.lower()
        if ext[0] == '.':
            ext = ext[1:]
        print("ext = %s" % ext)
        if ext == 'ipynb':
            full_jup_path = os.path.join(jup_folder, curfile)
            print("full_jup_path = %s" % full_jup_path)
            jup_cmd = "python3 -m webbrowser %s &" % full_jup_path
            os.system(jup_cmd)
        else:
            if rwkos.amiMac():
                cmd = "open %s &" % curfile
            else:
                # assume chromebook
                app = app_dict[ext]
                cmd = "%s %s &" % (app, curfile)
            print(cmd)
            os.system(cmd)
    
    

def write_prev_student(username):
    f = open(prev_student_fn, 'w')
    f.write(username)
    f.close()
    

def read_student_id():
    if not os.path.exists(prev_student_fn):
        return None
    else:
        f = open(prev_student_fn, 'r')
        lines = f.readlines()
        curuser = lines[0].strip()
        f.close()
        return curuser
 

def get_next_student_id(usernames):
    if not os.path.exists(prev_student_fn):
        index = 0
    else:
        prev_user = read_student_id()
        index = usernames.index(prev_user)
        index += 1
        
    # next student is indexed from user names
    next_bb = usernames[index]

    return next_bb
    

     
def get_assign_number(folder_name):
    q = assign_p.match(folder_name)
    if q is None:
        print("folder_name: %s" % folder_name)
    assert q is not None, "Problem with folder pattern: %s" % folder_name
    return int(q.group(2))


def get_assign_type(folder_name):
    q = assign_p.match(folder_name)
    assert q is not None, "Problem with folder pattern: %s" % folder
    type_str = q.group(1)
    return type_str


def find_valid_root():
    curdir = os.getcwd()
    print("curdir = %s" % curdir)

    #possible_bad_root = "/home/ryanwkrauss/445_ss21"
    #good_root = "/mnt/chromeos/GoogleDrive/MyDrive/Teaching/445_SS21"
    
    bad_root = "/Volumes/GoogleDrive/My Drive/Teaching/445_SS23"
    bad_root2 = "/Users/kraussry/Library/CloudStorage/GoogleDrive-ryanwkrauss@gmail.com/My Drive/Teaching/445_SS23"
    bad_roots = [bad_root, bad_root2]
    
    for bad in bad_roots:
        if bad in curdir:
            print("found: %s" % bad)
            rep_root = "/Users/kraussry/445_SS23"
            curdir = curdir.replace(bad, rep_root)
        else:
            print("%s not in %s" % (bad, curdir))
    
    return curdir
    

def find_csv_bb_files_walking_up(folder):
    csv_pats = ["gc_*.csv", "bb_*.csv"]

    csv_list = []

    for cpat in csv_pats:
        curlist = rwkos.glob_search_walking_up(folder,cpat)
        csv_list.extend(curlist)

    return csv_list


def find_csv_label_in_list_of_files(mypat, csv_list):
    mylabel=None

    for csv_path in csv_list:
        mylabel = find_bb_column_label(csv_path, mypat, debug=0) 
        if mylabel is not None:
            # stop first time we find it
            break
    
    return mylabel


def create_grading_csv(outpath, newlabel, bb_csv_path):
    df = bb_pandas_utils.open_clean_bb_csv_as_df(bb_csv_path)
    name_cols = ['Last Name', 'First Name', 'Username']
    name_df = df[name_cols]

    N = len(name_df.values)
    new_scores = ['']*N
    new_notes = ['']*N

    name_df[newlabel] = new_scores
    name_df["Notes"] = new_notes

    name_df.to_csv(outpath,index=False)


def chop_from_end(linkin):
    linkout = linkin
    for item in chop_list:
        if item in linkout:
            linkout, rest = linkout.split(item, 1)
    return linkout


d_file_types = ['file','presentation','document','spreadsheets']

def break_file_d_link(linkin, filetype='file'):
    splitstr = filetype + '/d/'
    base, linkid = linkin.split(splitstr,1)
    linkid = chop_from_end(linkid)
    return linkid


def break_folder_link(linkin):
    splitstr = '/folders/'
    base, linkid = linkin.split(splitstr,1)
    linkid = chop_from_end(linkid)
    return linkid
    

def get_file_id(linkin):
    match = False
    if "id=" in linkin:
        base, linkid = linkin.split("id=",1)
        match = True
    else:
        for item in d_file_types:
            search_str = "/" + item + "/"
            if search_str in linkin:
                match = True
                #pdb.set_trace()
                linkid = break_file_d_link(linkin, filetype=item)
                break

    if not match:
        folder_str = '/folders/'
        if folder_str in linkin:
            match = True
            linkid = break_folder_link(linkin)
        else:
            raise ValueError("Cannot work with this link: %s" % linkin)
    return linkid


def jupyter_notebook_gdrive_img_link(linkin, width=300):
    # goal: <img src="https://drive.google.com/uc?id=1sRRu8WPs9yBBOEC7OkComZfUd5P5h7CY" width=300px>
    pat = '<img src="https://drive.google.com/uc?id=%s" width=%ipx>'
    my_id = get_file_id(linkin)
    out_str = pat % (my_id, width)
    return out_str


def gdrive_url_builder(linkin):
    my_id = get_file_id(linkin)
    url = "https://drive.google.com/uc?id=%s" % my_id
    return url


def markdown_jupyter_download_link(linkin):
    my_id = get_file_id(linkin)
    download_str = "https://drive.google.com/uc?export=download&id=%s" % my_id  
    out_str = "[%s](%s)" % (download_str, download_str)
    return out_str


def download_for_gslides(linkin):
    my_id = get_file_id(linkin)
    download_str = "https://drive.google.com/uc?export=download&id=%s" % my_id  
    out_str = "%s" % download_str
    return out_str


def markdown_pdf_open_link(linkin):
    my_id = get_file_id(linkin)
    open_str = "https://drive.google.com/open?id=%s" % my_id
    out_str = '[%s](%s){target="_blank"}' % (open_str, open_str)
    return out_str


def pdf_link_download_maker(linkin):
    linkid = get_file_id(linkin)
    out_str = html_pdf_links_str.replace("IDSTR",linkid)
    print(out_str)


def pdf_link_download_maker_no_print(linkin):
    linkid = get_file_id(linkin)
    out_str = html_pdf_links_str.replace("IDSTR",linkid)
    return out_str


def pdf_link_download_only_no_print(linkin):
    linkid = get_file_id(linkin)
    out_str = download_only_str.replace("IDSTR",linkid)
    return out_str


def link_open_only_no_print(linkin):
    linkid = get_file_id(linkin)
    out_str = open_only_str.replace("IDSTR",linkid)
    return out_str


def link_open_link_only(linkin):
    linkid = get_file_id(linkin)
    out_str = open_link_only_str.replace("IDSTR",linkid)
    return out_str
    

def link_pure_open_no_print(linkin):
    linkid = get_file_id(linkin)
    out_str = pure_open_only_str.replace("IDSTR",linkid)
    return out_str


def youtube_link(linkin):
    out_str = pure_link_str.replace("MYPATH", linkin)
    return out_str

