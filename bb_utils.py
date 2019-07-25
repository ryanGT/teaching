import re
#import pdb

html_pdf_links_str = r"""<p>Open: <a href="https://drive.google.com/open?id=IDSTR" target="_blank">https://drive.google.com/open?id=IDSTR</a></p>
<p>Download: <a href="https://drive.google.com/uc?export=download&id=IDSTR" target="_blank">https://drive.google.com/uc?export=download&id=IDSTR</a></p>"""

download_only_str = r"""<p>Download: <a href="https://drive.google.com/uc?export=download&id=IDSTR" target="_blank">https://drive.google.com/uc?export=download&id=IDSTR</a></p>"""

open_only_str = r"""<p>Open: <a href="https://drive.google.com/open?id=IDSTR" target="_blank">https://drive.google.com/open?id=IDSTR</a></p>"""

pure_open_only_str = r"""<p><a href="https://drive.google.com/open?id=IDSTR" target="_blank">https://drive.google.com/open?id=IDSTR</a></p>"""

pure_link_str = r'<p><a href="MYPATH" target="_blank">MYPATH</a></p>'

## Two forms of gdrive links:
#https://drive.google.com/file/d/1zzY_zN6DJMCZtohuMc0lgB8gzxOE01u5/view?usp=sharing
#https://drive.google.com/open?id=1zzY_zN6DJMCZtohuMc0lgB8gzxOE01u5
#https://docs.google.com/presentation/d/1y4s2w0wuN_MBtho-84gKhbRnza-_04FqS6bNQI30mJg/edit?usp=sharing
#https://docs.google.com/presentation/d/1y4s2w0wuN_MBtho-84gKhbRnza-_04FqS6bNQI30mJg/edit?usp=sharing
#https://drive.google.com/drive/folders/1K1QvjItpjSvSh1Y9MlZY1fczrC94oO4C?usp=sharing
#https://docs.google.com/document/d/1HjKxcGE2ITonkNe9SFfcBUX6FhLYQBR4euhTESZe9Q4/edit?usp=sharing

chop_list = ["/view","/edit"]


def chop_from_end(linkin):
    linkout = linkin
    for item in chop_list:
        if item in linkout:
            linkout, rest = linkout.split(item, 1)
    return linkout


d_file_types = ['file','presentation','document']

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


def markdown_jupyter_download_link(linkin):
    my_id = get_file_id(linkin)
    download_str = "https://drive.google.com/uc?export=download&id=%s" % my_id  
    out_str = "[%s](%s)" % (download_str, download_str)
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


def link_pure_open_no_print(linkin):
    linkid = get_file_id(linkin)
    out_str = pure_open_only_str.replace("IDSTR",linkid)
    return out_str


def youtube_link(linkin):
    out_str = pure_link_str.replace("MYPATH", linkin)
    return out_str

