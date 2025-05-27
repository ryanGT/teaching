#!/usr/bin/python3

import sys
import argparse
import os.path
from subprocess import Popen,PIPE

def escape(s):
    """Escape backslashes and quotes to appease AppleScript"""
    s = s.replace("\\","\\\\")
    s = s.replace('"','\\"')
    return s

def make_message(content,subject=None,to_addr=None,from_addr=None,
    send=False,cc_addr=None,bcc_addr=None,attach=None):
    """Use applescript to create a mail message"""
    if send:
        properties = ["visible:false"]
    else:
        properties = ["visible:true"]
    if subject:
        properties.append('subject:"%s"' % escape(subject))
    if from_addr:
        properties.append('sender:"%s"' % escape(subject))
    if len(content) > 0:
        properties.append('content:"%s"' % escape(content))
    
    properties_string = ",".join(properties)

    template = 'make new %s with properties {%s:"%s"}'
    make_new = []
    if to_addr:
        make_new.extend([template % ("to recipient","address", escape(addr)) for addr in to_addr])
    if cc_addr:
        make_new.extend([template % ("cc recipient","address", escape(addr)) for addr in cc_addr])
    if bcc_addr:
        make_new.extend([template % ("bcc recipient","address", escape(addr)) for addr in bcc_addr])
    if attach:
        make_new.extend([template % ("attachment","file name", escape(os.path.abspath(f))) for f in attach])
    if send:
        make_new.append('send')
    if len(make_new) > 0:
        make_new_string = "tell result\n" + "\n".join(make_new) + \
        "\nend tell\n"
    else:
        make_new_string = ""

    script = """tell application "Mail"
    make new outgoing message with properties {%s}
    %s end tell
    """ % (properties_string, make_new_string)


    print("script:")
    print(script)

    # run applescript
    p = Popen('/usr/bin/osascript',stdin=PIPE,stdout=PIPE)
    p.communicate(script.encode()) # send script to stdin
    return p.returncode



#content = "Happy anniversary again"
#subject = "congrats - 2"
#to_add = ["ryanwkrauss@gmail.com"]
#from_addr = "kraussry@gvsu.edu"
#send = True

#make_message(content,subject=subject,to_addr=to_add,\
#             from_addr=from_addr,send=send)
