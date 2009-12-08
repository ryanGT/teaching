from txt_mixin import *
#import spreadsheet
import rwkos

item_titles = ["The course content was well organized.", \
               "The objectives of the course were clear.", \
               "Please rate the textbooks/manuals/workbooks.", \
               "This course was interesting and motivated you to want to learn more.", \
               "The instructor explained the material clearly.", \
               "The class time was used efficiently.", \
               "The instructor efficiently cleared up student difficulties with the course material.", \
               "The instructor was accessible outside of class.", \
               "The instructor's style/format was effective.", \
               "The instructor was open and helpful.", \
               "The assignments enhanced your learning.", \
               "The tests were reliable measures of your knowledge of the material.", \
               "The grading was fair.", \
               "You were provided with timely and helpful feedback about your performance.", \
               "Please rate the instructor's overall performance.", \
               "The amount of work was appropriate.", \
               "What percentage of class meetings did you attend?", \
               "Approximately how many hours did you work outside of class for each hour in class"]


class survey_item(object):
    def __init__(self, title, number, \
                 labels=None, descending=True):
        self.title = title
        self.number = number
        if labels is None:
            labels = ['Strongly Agree','Agree','Neutral', \
                      'Disagree','Strongly Disagree']
        self.labels = labels
        if descending:
            self.values = range(5,0,-1)
        else:
            self.values = range(1,6)
        

    def to_csv(self):
        self.list = ['"Item Analysis - Survey: %s: %s"' % (self.number, self.title)]
        out = self.list.append
        for curlabel, curval in zip(self.labels, self.values):
            row = '"%s", %s, ' % (curlabel, curval)
            out(row)
        out('"Total Valid", , ')
        out('"Total Missing", , 0')
        out('')
        return self.list
        

elist = ['Excellent','Good','Satisfactory','Fair','Poor']
einds = [3,15]

meetings_labels = ['Less than 60\\%', \
                   '60-70\\%', \
                   '70-80\\%', \
                   '80-90\\%', \
                   '90-100\\%']
hours_labels = ['Very Little Time', \
                '1 hour', \
                '2 hours', \
                '3 hours', \
                '$>$ 3 hours']

ascending_inds = [17,18]

if __name__ == '__main__':
    folder = rwkos.FindFullPath('siue/tenure/student_evaluations')
    filename = 'blank_item_analysis.csv'
    pathout = os.path.join(folder, filename)
    for n, title in enumerate(item_titles):
        i = n+1
        labels = None
        if i in einds:
            labels = elist
        elif i == 17:
            labels = meetings_labels
        elif i == 18:
            labels = hours_labels
        descending = True
        if i in ascending_inds:
            descending = False
        curitem = survey_item(title, i, labels=labels, descending=descending)
        curlist = curitem.to_csv()
        if i == 1:
            biglist = curlist
        else:
            biglist.extend(curlist)
    dump(pathout, biglist)
    
