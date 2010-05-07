class group(object):
    def __init__(self, group_name, group_list, alts={}):
        self.group_name = group_name
        self.group_list = group_list
        self.alts = alts
        self.find_members()

    def strip_names(self):
        self.firstnames = [item.strip() for item in self.firstnames]
        self.lastnames = [item.strip() for item in self.lastnames]

    def find_members(self):
        lastnames, firstnames = self.group_list.get_names(self.group_name)
        self.lastnames = lastnames
        self.firstnames = firstnames
        for n, lastname in enumerate(lastnames):
            if self.alts.has_key(lastname):
                self.firstnames[n] = self.alts[lastname]
        self.strip_names()
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
