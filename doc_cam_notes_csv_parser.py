import txt_mixin
import copy
#import pdb

class notes_csv_row(object):
    def process_row(self):
        """I am trying to elegantly handle commas in the title section.  This
           could happen with or without a link at the end of the list.
           The row is assumed to be in the form #pages,slide
           numbers,topic,link, where link is optional.  My plan is to
           pop pages, slide numbers, and possibly link from the list
           and whatever is left is the topic or subtitle or whatever.
        """
        self.raw_list = self.rowstr.split(',')
        temp_list = copy.copy(self.raw_list)
        assert len(temp_list) > 2, "csv row does not have enough elements: %s" % temp_list
        #print('temp_list = %s' % temp_list)
        self.pages = temp_list.pop(0)
        self.slide_str = temp_list.pop(0)
        try:
            self.slide_int = int(self.slide_str)
        except:
            self.slide_int = None
        #print('temp_list = %s' % temp_list)
        last_ent = temp_list[-1]
        if last_ent.find('https://drive.google.com/open') == 0:
            self.link = last_ent
            temp_list.pop(-1)
        else:
            self.link = None
        # what is left in temp list should now be just the title
        # - .join works even if there is just one entry
        self.title = ','.join(temp_list)
            
        
    def __init__(self, rowstr):
        self.rowstr = rowstr
        self.process_row()

        
class doc_cam_notes_csv_parser(txt_mixin.txt_file_with_list):
    def clean_list(self):
        header = []

        for i in range(100):
            if self.list[0][0] == '#':
                line0 = self.list.pop(0)
                header.append(line0)
            else:
                break
            
        self.header = header
        temp_list = [item.strip() for item in self.list]
        self.clean_list = list(filter(None,temp_list))
    
        
    def parse(self):
        self.clean_list()
        self.rows = [notes_csv_row(item) for item in self.clean_list]
        # handle the "all combined" row separately
        last_row = self.rows[-1]
        if last_row.pages == '-':
            self.all_comb_row = self.rows.pop(-1)
        else:
            self.all_comb_row = None
            

    def __init__(self, *args, **kwargs):
        txt_mixin.txt_file_with_list.__init__(self, *args, **kwargs)
        self.parse()

