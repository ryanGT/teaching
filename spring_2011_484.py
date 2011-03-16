import os
import rwkos, spreadsheet

monday_groups = ['Lead Shot Dripping System', \
                 'Solar Car Chassis', \
                 'Remote Controlled Retrieval Vehicle', \
                 'Telescope Shelter', \
                 'Baja Transaxle']

wednesday_groups = ['Mechanized Bicycle Rack and Storage', \
                    'Adjustable Ratio Rocker Arms', \
                    'Automatic Tennis Ball Shooter', \
                    'Foam Dart Claymore', \
                    'Trash Master', \
                    'Screw Gun Cooling System']

all_groups = monday_groups + wednesday_groups

class_folder = rwkos.FindFullPath('siue/classes/484/2011')
group_path = os.path.join(class_folder, 'group_list.csv')
group_list = spreadsheet.group_list(group_path)

alts = {'Bemrose-Fetter':'Rebecca', \
        'Brown':'Chris',\
        'Flahan':'Chris',\
        'Card':'Will',\
        'Dement':'Joe',\
        'Gehrs':'Ben',\
        'Graham':'Mike',\
        'Mulvey':'Dan',\
        'Hankins':'Matt',\
        'Pish':'Jill',\
        'Spihlman':'Andi',\
        'Thompson':'Luke',\
        'Woodrome':'Jon',\
        'Pirmann':'Tim'
        }

inverse_alts = {'Joe':'Joseph', \
                'Mike':'Michael', \
                'Luke':'Lucas', \
                'Andi':'Andrea', \
                'Matt':'Matthew',\
                'Jill':'Jillian'}

email_path = os.path.join(class_folder, 'email_list_editted.csv')
email_list = spreadsheet.email_list(email_path)


def make_filename(projectname):
    filename = projectname.replace(' ','_') + '.rst'
    return filename
