import make_class_list
reload(make_class_list)

import os

root = '/home/ryan/siue/classes/482/2010'
note = 'ME482 Fall 2010'

pathin1 = os.path.join(root, 'class_list_raw.csv')
pathout1 = pathin1.replace('_raw.csv','_out.csv')
#email_path = os.path.join(root, 'email_list_raw.csv')
mylist1 = make_class_list.class_list_maker(pathin1)
mylist1.run()

pathin2 = os.path.join(root, 'class_list_week2.txt')
pathout2 = pathin2.replace('_raw.csv','_out.csv')
#email_path = os.path.join(root, 'email_list_raw.csv')
mylist2 = make_class_list.class_list_maker(pathin2)
mylist2.run()

dropped = [item for item in mylist1.list if item not in mylist2.list]
added = [item for item in mylist2.list if item not in mylist1.list]
