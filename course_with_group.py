import txt_mixin

class group(object):
    def __init__(self, group_name, group_list, alts={}):
        self.group_name = group_name
        self.group_list = group_list
        self.alts = alts
        self.find_members()


    def strip_names(self):
        firstnames = [item.strip() for item in self.firstnames]
        lastnames = [item.strip() for item in self.lastnames]
        self.firstnames = txt_mixin.txt_list(firstnames)
        self.lastnames = txt_mixin.txt_list(lastnames)
        

    def find_members(self):
        lastnames, firstnames = self.group_list.get_names(self.group_name)
        self.lastnames = lastnames
        self.firstnames = firstnames
        for n, lastname in enumerate(lastnames):
            if self.alts.has_key(lastname):
                self.firstnames[n] = self.alts[lastname]
        self.strip_names()
        self.fix_dup_firsts()
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


    def fix_dup_firsts(self):
        for name in self.firstnames:
            inds = self.firstnames.findall(name)
            if len(inds) > 1:
                print('found dup.:' + name)
                for ind in inds:
                    initial = ' ' + self.lastnames[ind][0] + '.'
                    self.firstnames[ind] += initial

