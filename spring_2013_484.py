import os
import rwkos, spreadsheet

monday_groups = ["Automated Brewing System", \
                 "Arrowsheds", \
                 "Dampening Vehicle Seat", \
                 "FSAE Paddle Shift", \
                 ]



wednesday_groups = ["Piston Driven Rifles", \
                    "Turner Electric Switch", \
                    "Rankine Power Cycle", \
                    "ASHRAE Portable Refrigerator", \
                    "Mobile Solar Array", \
                   ]

all_groups = monday_groups + wednesday_groups

class_folder = rwkos.FindFullPath('siue/classes/484/2013')
group_path = os.path.join(class_folder, 'group_list.csv')
group_list = spreadsheet.group_list(group_path)

alts = {'Bahrns':'Chris', \
        'Barnes':'Alex', \
        'Casey':'Jeff', \
        'Knauer':'Chris', \
        'Phillips':'Joe', \
        'Rickert':'Chris', \
        'Fehrenbacher':'Joe', \
        'Coleman':'Matt', \
        'Tripp':'Matt', \
        'Sprehe':'Dan', \
        'Strackeljahn':'Dan', \
        }

inverse_alts = {'Chris':'Christopher', \
                'Joe':'Joseph', \
                'Alex':'Alexander', \
                }

email_path = os.path.join(class_folder, 'email_list.csv')
email_list = spreadsheet.email_list(email_path)


def make_filename(projectname):
    filename = projectname.replace(' ','_') + '.rst'
    return filename
