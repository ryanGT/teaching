import os
import rwkos, spreadsheet

monday_groups = ["ASHRAE Design Competition", \
                 "Multipurpose Auger", \
                 "Baja Frame Design", \
                 "Portable Refrigerator", \
                 ]



wednesday_groups = ["Arnold Press", \
                    "Dyno", \
                    "Winglet Design", \
                    "Adjustable Desk", \
                   ]

all_groups = monday_groups + wednesday_groups

class_folder = rwkos.FindFullPath('siue/classes/484/2012')
group_path = os.path.join(class_folder, 'group_list.csv')
group_list = spreadsheet.group_list(group_path)

alts = {'Grahek':'Nick', \
        'Hall':'Matt', \
        'Luebcke':'Kim', \
        'Luly':'Ben', \
        'Jeffery':'Benny', \
        'Parker':'Logan', \
        'Donlan':'Zach', \
        'Hake':'Cliff', \
        #'Clabby':'Nate', \
        'Raube':'Zack', \
        }

inverse_alts = {'Kim':'Kimberly', \
                'Ben':'Benjamin', \
                'Benny':'Benjamin', \
                'Nick':'Nicholas', \
                'Matt':'Matthew', \
                'Logan':'Richard', \
                'Zach':'Zachary', \
                'Zack':'Zachary', \
                'Cliff':'Clifton', \
                'Nate':'Nathan', \
                }

email_path = os.path.join(class_folder, 'email_list.csv')
email_list = spreadsheet.email_list(email_path)


def make_filename(projectname):
    filename = projectname.replace(' ','_') + '.rst'
    return filename
