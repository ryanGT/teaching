import os
import rwkos, spreadsheet

monday_groups = ['Motorized Hand Truck', \
                 'Beverage Launching Refrigerator', \
                 'Green Refrigeration', \
                 'Upright Wheelchair', \
                 'Swirl Generator']

wednesday_groups = ['Mechanized Tree Stand', \
                    'Autonomous Vehicle', \
                    'Simplified Water Purification',\
                    'Cougar Baja', \
                    'Green Pedaling', \
                    'Hydraulic Bicycle Transmission']

all_groups = monday_groups + wednesday_groups

class_folder = rwkos.FindFullPath('siue/classes/484/2010')
group_path = os.path.join(class_folder, 'group_list.csv')
group_list = spreadsheet.group_list(group_path)

alts = {'Trutter':'Ben','Herren':'Zach', 'Schelp':'Tim', \
        'Tolbert':'Chris', 'Bailey':'Matt', \
        'Schutte':'Joe','Knepper':'Nick', 'Niccum':'Jake', \
        'Sansone':'Vinnie', 'Loucks':'Nate'}

email_path = os.path.join(class_folder, 'class_list.csv')
email_list = spreadsheet.email_list(email_path)


def make_filename(projectname):
    filename = projectname.replace(' ','_') + '.rst'
    return filename
