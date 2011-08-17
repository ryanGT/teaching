"""This module creates a dictionary of all the semesters since my
teachingn career started with the strings as keys ('Fall 2006',
'Spring 2007', ...) and the indexes as keys (0,1,...).  The indexes
will be used to plot a student evaluation score over time."""
semesters = []
prev_sem = 'Summer'
prev_year = 2006

for i in range(45):
    if prev_sem == 'Spring':
        sem = 'Summer'
        year = prev_year
    elif prev_sem == 'Summer':
        sem = 'Fall'
        year = prev_year
    elif prev_sem == 'Fall':
        sem = 'Spring'
        year = prev_year + 1
    semesters.append(sem+' '+str(year))
    prev_sem = sem
    prev_year = year

semester_dict = dict(zip(semesters, range(len(semesters))))
inv_semester_dict = dict((v,k) for k, v in semester_dict.iteritems())

