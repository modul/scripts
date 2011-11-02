# 
# abook2bdayreminders.py
#
# This script takes your addressbook in CSV format (delimiter should be a comma)
# and looks for the birthdates of your contacts. If some were found, the script
# generates a reminder file (in `remind` syntax) to remind you of these
# birthdays.
# The CSV file should be comma-delimited and must contain field names in the
# first row. You may have to change the default fieldnames below.
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42): 
# <mo@liberejo.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
#
#  author: Remo Giermann 
# created: 2010/5/28
#

import csv
import time
import sys
import os.path

fieldnames = { \
'bday': 'Geburtstag', 'nick': 'Nick Name', 'name': 'Formatted Name' \
}
birthdate_delimiter = '-'
nickname_delimiter = ','

reminderline = "REM %s %2i +7 MSG %s turns [year(current()) - %i] %%b!%%"

monthnames = [ \
'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', \
'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def usage():
    print "%s FILE" % sys.argv[0]
    print
    print "This script takes your CSV addressbook and prints out"
    print "reminders for the birthdays of your contacts"
    print "Remo Giermann - 2010-05-28"


def checkfieldnames(fields):
    return fieldnames['bday'] in fields \
    and fieldnames['nick'] in fields \
    and fieldnames['name'] in fields


def sortlines(x, y):
    x = x.split()
    y = y.split()
    xmon = monthnames.index(x[1])
    ymon = monthnames.index(y[1])
    xday = int(x[2])
    yday = int(y[2])
    
    if xmon > ymon:
        return 1
    elif xmon < ymon:
        return -1
    else:
        if xday > yday:
            return 1
        elif xday < yday:
            return -1
        else:
            return 0
   

def parsefile(fname):
    fp = open(fname, 'r')
    reader = csv.DictReader(fp)
    
    if not checkfieldnames(reader.fieldnames):
        print "Not all defined fieldnames could be found in CSV file `%s`!" \
         % (fname)
        sys.exit(1)
        
    names, bdays, nicks = [], [], []
    lines = []
    
    for i in reader:
        names.append(i[fieldnames['name']])
        bdays.append(i[fieldnames['bday']])
        nicks.append(i[fieldnames['nick']])
    
    for i in range(len(bdays)):
        if bdays[i] is not '':
            birthdate = bdays[i].split(birthdate_delimiter)
        
            if nicks[i] is not '':
                resultname = nicks[i].split(nickname_delimiter)[0]
            elif names[i] is not '':
                resultname = names[i]
            else:
                resultname = "Unknown"
            
            resultname = resultname.title()
            
            themonth = monthnames[int(birthdate[1]) - 1]
            theyear  = int(birthdate[0])
            theday   = int(birthdate[2])
           
            lines.append(reminderline % (themonth, theday, resultname, theyear))
    
    return lines
   

argc = len(sys.argv)

if argc == 1:
    usage()
    sys.exit(1)

else:
    if not os.path.isfile(sys.argv[1]):
        print "Cannot open file `%s`" % sys.argv[1]
        sys.exit(1)
    
    else:
        lines = parsefile(sys.argv[1])
        lines.sort(cmp=sortlines)
        for l in lines:
            print l
        sys.exit(0)
    