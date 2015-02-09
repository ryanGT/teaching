import os
import rwkos, spreadsheet

tuesday_groups = ['Oil Filter Crusher', \
                  'Streamline Home Brewhaus', \
                  'Portable Biomass Stove and Solar Powered Furnace', \
                 ]


thursday_groups = ['Ball Striking Machine', \
                   'Sidewalk Inspector Robot', \
                   'Active Suspension Research', \
                   ]

all_groups = tuesday_groups + thursday_groups

class_folder = rwkos.FindFullPath('siue/classes/484/Fall_2014')
group_path = os.path.join(class_folder, 'group_list.csv')
group_list = spreadsheet.group_list_2010(group_path)

#group_path = os.path.join(class_folder, 'planning/mini_project/team_list.csv')
#group_list = spreadsheet.mini_project_group_list(group_path)

alts = {'Prause':'Scott', \
        'Little':'Greg', \
        'Fulk':'Greg', \
        }

inverse_alts = {'Greg':'Gregory', \
                'Scott':'Randolph', \
                }

email_path = os.path.join(class_folder, 'email_list.csv')
email_list = spreadsheet.email_list(email_path)


def make_filename(projectname):
    filename = projectname.replace(' ','_') + '.rst'
    return filename
