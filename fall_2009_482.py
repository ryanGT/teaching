import os, rwkos, spreadsheet

class_folder = rwkos.FindFullPath('siue/classes/482/2009/group_grades')
group_path = os.path.join(class_folder, 'group_list.csv')
group_list = spreadsheet.group_list(group_path)

alts = {'Trutter':'Ben','Herren':'Zach', 'Schelp':'Tim', \
        'Tolbert':'Chris', 'Bailey':'Matt', \
        'Schutte':'Joe'}



def file_name_from_group_name(group_name, ext='.rst'):
    filename = group_name.replace(' ','_') + ext
    return filename
    

class group(object):
    def __init__(self, group_name):
        self.group_name = group_name
        self.find_members()


    def find_members(self):
        lastnames, firstnames = group_list.get_names(self.group_name)
        self.lastnames = lastnames
        self.firstnames = firstnames
        for n, lastname in enumerate(lastnames):
            if alts.has_key(lastname):
                self.firstnames[n] = alts[lastname]
        self.names = zip(self.firstnames, self.lastnames)


    def build_name_str(self):
        N = len(self.names)
        if N == 1:
            self.name_str = ' '.join(self.names[0])
        else:
            name_str = ''
            for n, pair in enumerate(self.names):
                if n > 0:
                    name_str +=', '
                if n == (N-1):
                    name_str += 'and '
                name_str += pair[0] + ' ' + pair[1]
            self.name_str = name_str

        
