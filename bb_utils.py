import re

html_pdf_links_str = r"""<p>Open: <a href="https://drive.google.com/open?id=IDSTR" target="_blank">https://drive.google.com/open?id=IDSTR</a></p>
<p>Download: <a href="https://drive.google.com/uc?export=download&id=IDSTR" target="_blank">https://drive.google.com/uc?export=download&id=IDSTR</a></p>"""


def pdf_link_download_maker(linkin):
    base, linkid = linkin.split("id=",1)
    out_str = html_pdf_links_str.replace("IDSTR",linkid)
    print(out_str)




