#!/usr/bin/env python
"""This module adds up the points in a tex exam file by looking for
lines that start with \item(xx points)"""
import txt_mixin, re

from optparse import OptionParser

usage = 'usage: %prog [options] tex_file_name'
parser = OptionParser(usage)


## parser.add_option("-c", "--case", dest="case", \
##                   help="A string containing the list of cases to run:\n" +
##                   "1 = siue office ssh \n 2 = home ssh \n" + \
##                   "3 = CORSAIR Fall 2010 \n 4 = IOMEGA Fall 2010", \
##                   default='12', type="string")

## parser.add_option("-p", action="store_true", dest="set_perms", \
##                   help="set website permissions")
## parser.set_defaults(set_perms=False)

(options, args) = parser.parse_args()

filename = args[0]

myfile = txt_mixin.txt_file_with_list(filename)

pat = '^\\\\item \\(([0-9]+) points\\)'
p = re.compile(pat)

inds = myfile.findallre(pat)

assert len(inds) > 0, "Did not find any lines that start with \\item (xx points)"

total = 0

for i, ind in enumerate(inds):
    curline = myfile.list[ind]
    q = p.search(curline)
    curpoints = int(q.group(1))
    print('Problem %i: %s points' % (i+1, curpoints))
    total += curpoints

print('----------------')
print('Total = %s' % total)
