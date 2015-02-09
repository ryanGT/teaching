================================
 Notes for Assessing ME 482/484
================================


Spring 2012
~~~~~~~~~~~~~~~~


Team Member Assessment
==========================

For the areas that are assessed based on team member ratings, go to
the folder ~/git/teacting and run the script
assess_482_484_from_team_member_ratings.py.  There are two cases, one
for 482 and one for 484 (you have to run the script once for each
case).  This should output two csv files into the 484/year/assessment
folder:

- assessment_from_482_team_member_ratings.csv
- assessment_from_484_team_member_ratings.csv

These files contain ratio of each student to the team average.  These
ratios have to be processed to convert them to 1, 3, or 5 scores.



New Main Script
===============


I am trying to automate the assessment process more so that the data
is automatically retrieved from the various csv files.  The new main
script is in the folder ~/git/teaching and is called
main_482_482_assessment_script.py.  It uses the module
assessment_processing_482_484.py for most of the actual processing
(this module is also in ~/git/teaching).


Manual Stuff
============


Some stuff hasn't been completely automated.  These things need to be done by hand:

- A file called bb_assessment.csv must exist in the 484/assessment
  folder.  Be sure it is really comma delimited and the first label is
  "Last Name" - BlackBoard or openoffice seems to screw this up.
- A file called assessment_report_header.tex will be copied into the
  484/assessment directory, but its header/footer years do not
  automatically update (yet).
- The 482 proposal grades have 2 columns labeled "Design Strategy"
  grades.  For assessment, we want the second one.  I manually changed
  the column label of the first one to "Design Strategy (sub
  category)" so that it doesn't match.
- For this year, I also created the file
  speaking_and_delivery_final_assessment.csv by hand.  It is in the
  484/assessment folder.
- the final assessment_summary_482_484_2011_2012.ods is created by
  doing the formatting of the csv file by hand in LibreOffice
- I hand copied the file assessment_report.pdf to
  assessment_report_ME_482_484_2011_2012AY.pdf
