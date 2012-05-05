import numpy

from numpy import where

from IPython.Debugger import Pdb

import assessment_processing_482_484 as AP
reload(AP)

import os, rwkos, spreadsheet, time, txt_mixin

year_str = time.strftime('%Y')
year_int = int(year_str)
prev_year = year_int - 1
prev_year_str = '%i' % prev_year

relpath_482 = 'siue/classes/482/' + prev_year_str
relpath_484 = 'siue/classes/484/' + year_str
root_482 = rwkos.FindFullPath(relpath_482)
root_484 = rwkos.FindFullPath(relpath_484)

assessment_folder = os.path.join(root_484,'assessment')

bb_in_path = os.path.join(assessment_folder, 'bb_assessment.csv')
bb = AP.BB_file_482_assessment(bb_in_path)

import compile_course_grades

import copy

#load last year's summary file
last_years_path = '/home/ryan/siue/classes/484/2011/assessment/rwk_assessment_482_484_2010_2011_summary.csv'
colmap = {'Item':'item','Ave. Score':'ave_score', \
          'Exceeds':'num_exceeds',\
          'Meets':'num_meets',\
          'Does Not Meet':'num_does_not_meet'}

last_years_sheet = spreadsheet.SpreadsheetFromPath(last_years_path, \
                                                   colmap=colmap)

last_years_sheet.FindLabelRow('Item')#this is the upper left column label
#note you could  also pass in a list
last_years_sheet.FindDataColumns()
last_years_sheet.MapCols()

big_csv_labels = ['"Item #"', \
                  '"Description"', \
                  '"Exceeds expectation (5)"', \
                  '"Meets expectation (3)"', \
                  '"Does not meet expectation (1)"', \
                  '"Ave. Score"', \
                  '"Exceeds"', \
                  '"Meets"', \
                  '"Does Not Meet"', \
                  '"Previous Year Ave. Score"', \
                  ]
last_years_ave = last_years_sheet.ave_score.astype('float')

#make a dictionary with the number of members in each group
import rwkmisc
modname = 'spring_%s_484' % year_str
mymod = rwkmisc.my_import(modname)

group_list = mymod.group_list
alts = mymod.alts

group_names = mymod.group_list[1]
team_names = group_names
member_list = mymod.group_list[2]
number_of_members = [0]*len(group_names)

for i, cur_members in enumerate(member_list):
    cur_list = cur_members.split(',')
    cur_num = len(cur_list)
    number_of_members[i] = cur_num

group_members_dict = dict(zip(group_names, number_of_members))

big_item_list = []

#Item 1
## description = 'Design strategy [c]'

## exceeds_criteria = 'Carefully plans and sets objectives as well as how to achieve the objectives. Readily uses alternative methods when necessary.'

## meets_criteria = 'Plans and sets objectives, but how to achieve the objectives is not clearly stated. There is no alternative method proposed.'

## does_not_meet_criteria = 'Does not have a working design strategy.'

## source = '482 proposal paper Design Strategy grade'
## exceeds_cutoff = 8.99
## meets_cutoff = 7.6
## does_not_meet_cutoff = 0.0

## relpath = 'group_grades/proposal_grades/proposal_grades.csv'
## col_label = 'Design Strategy'

## proposal_name_label = 'Group Name'
## proposal_csv_path = os.path.join(root_482, relpath)

## gc = compile_course_grades.course_grade_compiler_team(proposal_csv_path, name_label='Group Name')

## sheet_1 = gc.retrieve_one_grade(proposal_csv_path, 'Design Strategy')
## raw_scores_1 = numpy.squeeze(sheet_1.values)

## kwargs = {'subtitle':description, \
##           'source':source, \
##           'exceeds_criteria':exceeds_criteria, \
##           'meets_criteria':meets_criteria, \
##           'does_not_meet_criteria':does_not_meet_criteria}

## item1 = AP.team_item_2012(1, team_names, number_of_members, \
##                           raw_scores_1, exceeds_cutoff, meets_cutoff, **kwargs)

## big_item_list.append(item1)


#Item 2
## description = 'Background research: Literature Review [c, h]'

## exceeds_criteria = 'Finds 5 or more scholarly articles that are closely related to the project; thoroughly discusses the connection between those articles and the project'

## meets_criteria = 'Finds 3 or more scholarly articles closely related to the project  and at least two other sources that are either not scholarly or not closely  related; discussion of sources is fairly thorough'

## does_not_meet_criteria = 'Finds less than 3 closely related scholarly articles or the discussion of the articles is cursory'

## source = '482 proposal paper Literature Review grade'
## exceeds_cutoff = 8.99
## meets_cutoff = 7.6
## does_not_meet_cutoff = 0.0

## relpath = 'group_grades/proposal_grades/proposal_grades.csv'
## col_label = 'Design Strategy'

## proposal_name_label = 'Group Name'
## proposal_csv_path = os.path.join(root_482, relpath)

## gc = compile_course_grades.course_grade_compiler_team(proposal_csv_path, name_label='Group Name')

## sheet_1 = gc.retrieve_one_grade(proposal_csv_path, 'Design Strategy')
## raw_scores_1 = numpy.squeeze(sheet_1.values)

## kwargs = {'subtitle':description, \
##           'source':source, \
##           'exceeds_criteria':exceeds_criteria, \
##           'meets_criteria':meets_criteria, \
##           'does_not_meet_criteria':does_not_meet_criteria}

## item1 = AP.team_item_2012(1, team_names, number_of_members, \
##                           raw_scores_1, exceeds_cutoff, meets_cutoff, **kwargs)

## big_item_list.append(item1)



#Load Assessment Info
info_col_map = {"Item #": 'item_num', \
                "Description":'description', \
                "Exceeds Criteria": 'exceeds_criteria', \
                "Meets Criteria": 'meets_criteria', \
                "Does Not Meet Criteria": 'does_not_meet_criteria', \
                "Source": 'source', \
                "Exceeds Cutoff": 'exceeds_cutoff', \
                "Meets Cutoff": 'meets_cutoff', \
                "Team Item": 'team_item', \
                "Survey Item": 'survey_item', \
                "Individual Item": 'individual_item', \
                "Question": 'question', \
                }
info_path = 'assessment_info_482_484.csv'
info_sheet = spreadsheet.SpreadsheetFromPath(info_path, \
                                             colmap=info_col_map)

info_sheet.FindLabelRow('Item #')#this is the upper left column label
#note you could  also pass in a list
info_sheet.FindDataColumns()
info_sheet.MapCols()

proposal_name_label = 'Group Name'
proposal_relpath = 'group_grades/proposal_grades/proposal_grades.csv'
proposal_csv_path = os.path.join(root_482, proposal_relpath)

survey_name_label = 'Last Name'
team_member_ratings_482_relpath = 'assessment/assessment_from_482_team_member_ratings.csv'
team_member_ratings_482_path = os.path.join(root_484, team_member_ratings_482_relpath)

team_member_ratings_484_relpath = 'assessment/assessment_from_484_team_member_ratings.csv'
team_member_ratings_484_path = os.path.join(root_484, team_member_ratings_484_relpath)

final_report_relpath = 'final_report_grades/final_report_grades.csv'
final_report_path = os.path.join(root_484, final_report_relpath)

ethics_relpath = 'group_grades/ethical_issues_and_societal_impacts.csv'
ethics_path = os.path.join(root_482, ethics_relpath)

speaking_and_delivery_relpath = 'assessment/speaking_and_delivery_final_assessment.csv'
speaking_and_delivery_path = os.path.join(root_484, speaking_and_delivery_relpath)

LLL_csv_relpath = 'LLL_grading_and_assessment.csv'
LLL_csv_path = os.path.join(root_484, LLL_csv_relpath)


csv_path_dict = {1:proposal_csv_path, \
                 2:proposal_csv_path, \
                 3:proposal_csv_path, \
                 4:team_member_ratings_482_path, \
                 5:team_member_ratings_482_path, \
                 6:team_member_ratings_484_path, \
                 7:ethics_path, \
                 8:team_member_ratings_484_path, \
                 9:proposal_csv_path, \
                 10:final_report_path, \
                 11:final_report_path, \
                 12:final_report_path, \
                 13:speaking_and_delivery_path, \
                 14:speaking_and_delivery_path, \
                 15:speaking_and_delivery_path, \
                 16:speaking_and_delivery_path, \
                 17:speaking_and_delivery_path, \
                 18:ethics_path, \
                 19:proposal_csv_path, \
                 20:LLL_csv_path, \
                 21:LLL_csv_path, \
                 22:final_report_path, \
                 }

name_label_dict = {1:proposal_name_label, \
                   2:proposal_name_label, \
                   3:proposal_name_label, \
                   4:survey_name_label, \
                   5:survey_name_label, \
                   6:survey_name_label, \
                   7:proposal_name_label, \
                   8:survey_name_label, \
                   9:proposal_name_label, \
                   10:proposal_name_label, \
                   11:proposal_name_label, \
                   12:proposal_name_label, \
                   13:survey_name_label, \
                   14:survey_name_label, \
                   15:survey_name_label, \
                   16:survey_name_label, \
                   17:survey_name_label, \
                   18:proposal_name_label, \
                   19:proposal_name_label, \
                   20:survey_name_label, \
                   21:survey_name_label, \
                   22:proposal_name_label, \
                   }

column_label_dict = {1:'Design Strategy', \
                     2:'Literature Review', \
                     3:'Constraints', \
                     4:'Attendance', \
                     5:'Participation', \
                     6:'Contribution of Ideas', \
                     7:'Ethics Assessment', \
                     8:'Teamwork', \
                     9:'Problem Statement and Formulation', \
                     10:'Organization and Flow', \
                     11:'Format/Style', \
                     12:'Grammar and Spelling', \
                     13:'Appearance', \
                     14:'Delivery', \
                     15:'Features', \
                     16:'Use of Visual Aides', \
                     17:'Listening to and Answering Questions', \
                     18:'Societal Impact Assessment', \
                     19:'Contemporary Issues', \
                     20:'Recognizes the Need for LLL (assessment)', \
                     21:'Is prepared to engage in LLL (assessment)', \
                     22:'Computers and Software', \
                     }
                   
    
items = range(1,23)

team_item = info_sheet.team_item.astype(float)
survey_item = info_sheet.survey_item.astype(float)
individual_item = info_sheet.individual_item.astype(float)
                                                    
for item in items:
    i = item-1
    cur_csv_path = csv_path_dict[item]
    name_label = name_label_dict[item]
    column_label = column_label_dict[item]
    gc = compile_course_grades.course_grade_compiler_team(cur_csv_path, \
                                                          name_label=name_label)

    sheet_1 = gc.retrieve_one_grade(cur_csv_path, column_label)
    raw_scores_1 = numpy.squeeze(sheet_1.values)

    kwargs = {'subtitle':info_sheet.description[i], \
              'source':info_sheet.source[i], \
              'exceeds_criteria':info_sheet.exceeds_criteria[i], \
              'meets_criteria':info_sheet.meets_criteria[i], \
              'does_not_meet_criteria':info_sheet.does_not_meet_criteria[i]}

    exceeds_cutoff = float(info_sheet.exceeds_cutoff[i])
    meets_cutoff = float(info_sheet.meets_cutoff[i])

    if team_item[i]:
        item1 = AP.team_item_2012(item, team_names, number_of_members, \
                                  raw_scores_1, \
                                  exceeds_cutoff, \
                                  meets_cutoff, \
                                  **kwargs)

    elif survey_item[i]:
        question = info_sheet.question[i]
        item1 = AP.survey_item_2012(item, question,
                                    bb.lastnames, \
                                    raw_scores_1, \
                                    exceeds_cutoff, \
                                    meets_cutoff, \
                                    firstnames=bb.firstnames, \
                                    **kwargs)

    elif individual_item[i]:
        item1 = AP.individual_item_2012(item, \
                                        bb.lastnames, \
                                        raw_scores_1, \
                                        exceeds_cutoff, \
                                        meets_cutoff, \
                                        firstnames=bb.firstnames, \
                                        **kwargs)

    
    big_item_list.append(item1)
    

def _csv_quote_string(str_in):
    str_out = copy.copy(str_in)
    quote_list = ['"', "'"]
    #clean quotes if they are already there
    if str_out[0] in quote_list:
        str_out = str_out[1:]
    if str_out[-1] in quote_list:
        str_out = str_out[0:-1]
    return '"' + str_out + '"'
        

def build_summary_row(i, cur_item, ave, \
                      num_exceeds, num_meets, num_does_not_meet):
    prev_ave = last_years_ave[i-1]    
    big_row = ['%i' % i, \
               _csv_quote_string(cur_item.subtitle), \
               _csv_quote_string(cur_item.exceeds_criteria), \
               _csv_quote_string(cur_item.meets_criteria), \
               _csv_quote_string(cur_item.does_not_meet_criteria), \
               ave, \
               num_exceeds, \
               num_meets, \
               num_does_not, \
               prev_ave]
    ## big_row = ['%i' % i, \
    ##            cur_item.subtitle, \
    ##            cur_item.exceeds_criteria, \
    ##            cur_item.meets_criteria, \
    ##            cur_item.does_not_meet_criteria, \
    ##            ave, \
    ##            num_exceeds, \
    ##            num_meets, \
    ##            num_does_not, \
    ##            prev_ave]
    return big_row


def dumpcsv(nested_list, pathout):
    listout = []
    for row in nested_list:
        str_list = [str(item) for item in row]
        row_str = ','.join(str_list)
        listout.append(row_str)
    txt_mixin.dump(pathout, listout)


#output csv and latex
if __name__ == '__main__':
    scr_dir = '/home/ryan/git/teaching/'
    header_name = 'assessment_report_header.tex'
    
    dst_path = os.path.join(assessment_folder, header_name)
    if not os.path.exists(dst_path):
        src_path = os.path.join(scr_dir, header_name)
        import shutil
        shutil.copyfile(src_path, dst_path)
    
    latex_out = ['\\input{assessment_report_header}', \
                 '\\begin{document}', \
                 '\\flushleft']

    big_spreadsheet_list = []
    big_spreadsheet_list.append(big_csv_labels)
    
    csvoutname = 'assessment_482_484_%s_%s_ind_mapped.csv' % (prev_year_str, year_str)
    csvoutpath = os.path.join(assessment_folder, csvoutname)
    #items = range(1,23)
    #items = [1]
    #items = [1,2,3]
    #items = [4]
    labels = ['Item %i' % item for item in items]
    bb.labels.extend(labels)
    #'Zackrie', 'Quince', 'qzackri'
    ave_row = ['','','Average']
    exceeds_row = ['','','Exceeds']
    meets_row = ['','','Meets']
    does_not_row = ['','','Does Not Meet']
    total_row = ['','','Total']

    for i in items:
        cur_item = big_item_list[i-1]
        #cur_item = item_parser(clean_path, i)
        #parsed_item = cur_item.parse_data()#<-- what methods and properties does a parsed_item need?

        col_label = 'Item %i' % i

        if isinstance(cur_item, AP.team_item_2012):
            for group_name, score in zip(cur_item.team_names, cur_item.scores):
                cur_group = AP.group(group_name, group_list, \
                                     item_number=i, score=score, alts=alts) 
                cur_group.insert_grades_into_bb(bb)

        else:
            bb.InsertColFromList_v2(cur_item.lastnames, cur_item.firstnames, \
                                    col_label, cur_item.scores, \
                                    verbosity=2)



        attr = 'item_%i' % i
        bb.assign_col_to_attr(col_label, attr)
        cur_data = getattr(bb, attr)
        ave = cur_data.mean()
        num_exceeds = len(where(cur_data==5)[0])
        num_meets = len(where(cur_data==3)[0])
        num_does_not = len(where(cur_data==1)[0])
        total = num_exceeds + num_meets + num_does_not

        ave_row.append(ave)
        exceeds_row.append(num_exceeds)
        meets_row.append(num_meets)
        does_not_row.append(num_does_not)
        total_row.append(total)

        big_row = build_summary_row(i, cur_item, ave, \
                                    num_exceeds, num_meets, \
                                    num_does_not)
        
        big_spreadsheet_list.append(big_row)
        
        if i > 0:
            latex_out.append('\\pagebreak')

        latex_out.extend(cur_item.to_latex(blanknames=False))
        latex_out.extend(AP.summary_row(ave, num_exceeds, \
                                        num_meets, num_does_not))
        ## for pname in project_names[0:1]:
        ##     cur_group = group(pname, group_list, alts=alts)
        ##     cur_group.()
        ##     cur_group.insert_grades_into_bb(bb)
        #--------------------------------
##         bb.InsertColFromList(cur_group.lastnames, 'Team Factor', \
##                              cur_group.team_factors, splitnames=0, \
##                              verbosity=1)
    #bb.run('combined_grades_out.csv')
    new_rows = [ave_row, exceeds_row, meets_row, does_not_row, total_row]
    for item in new_rows:
        bb.alldata.append(item)

    latex_out.append('\\end{document}')
    #texout = 'assessment_report_no_names.tex'
    texout = 'assessment_report.tex'
    texoutpath = os.path.join(assessment_folder, texout)
    txt_mixin.dump(texoutpath, latex_out)
    bb.save(csvoutpath)

    big_summary_out_name = 'assessment_summary_482_484_%s_%s.csv' % (prev_year_str, year_str)
    big_summary_path = os.path.join(assessment_folder, big_summary_out_name)
    dumpcsv(big_spreadsheet_list, big_summary_path)
    
