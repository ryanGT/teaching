"""Creating email lists for my classes based on the banner website is
annoying.  How to handle this on a Mac is apparently also a little
tricky.  So, I am tweaking it again.  I think the main Mac issue is
that clicking on the email class link opens the link in the mail app
which fills in the names of people whose email addesses are found.  My
code for making an email list assumes the names are not present.

I would like to write a function that takes a list of text which may
or may not contain line breaks or more than one email per line and
clean it up.  The code should also remove any names in the email
string."""
#jbargie@siue.edu, cbranch@siue.edu, jdennin@siue.edu, lyhogan@siue.edu, bkasmar@siue.edu, mostroo@siue.edu, bsaligr@siue.edu, pwollen@siue.edu, Derek Briesacher <dbriesa@siue.edu>, Patrick Buller <pbuller@siue.edu>, thartna@siue.edu, Gregory Jacobs <gjacobs@siue.edu>, cjames@siue.edu, jkutz@siue.edu, dowens@siue.edu, Austin Schukar <aschuka@siue.edu>, jstilt@siue.edu

import re
p = re.compile('<(.*)>')

def clean_one_email(email_in):
    email_out = email_in.strip()
    if email_out.find('<') > -1:
        q = p.search(email_out)
        if q is not None:
            email_out = q.group(1)
    return email_out


def clean_raw_emails(txtlist_in, delim=','):
    """Take a list of text lines and return a list containing one
    email per line.  Remove names if they are present.  Break lines
    that contain delim into lists."""
    if type(txtlist_in) == str:
        txtlist_in = [txtlist_in]

    all_emails = []

    for line in txtlist_in:
        cur_list = line.split(delim)
        cur_clean = [clean_one_email(item) for item in cur_list]
        all_emails.extend(cur_clean)

    return all_emails


def find_one_email(lastname, firstname, email_list):
    last = lastname.lower()
    first = firstname.lower()

    Nf = len(first)

    i = 1

    N = 7

    while i < Nf:
        fi = first[0:i]
        full = fi + last
        if len(full) > N:
            full = full[0:N]

        inds = email_list.findall(full)
        if not inds:
            i += 1
        else:
            if len(inds) > 1:
                matchstr = ''
                for ind in inds:
                    matchstr += email_list[ind] + ' '
            assert len(inds) == 1, 'Found more than one match for %s, matches: %s' % (full, matchstr)
            return email_list[inds[0]]
