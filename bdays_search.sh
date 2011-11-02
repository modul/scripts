#!/bin/bash
#
# search the datafile of bdays.awk
# 2004/04/13
#


FILE="$HOME/.bdays" # Yes, it may not exist
STR=$1  # Yes, it may be empty
	
cat $FILE | \
awk -F : '/'$STR'/ {printf("%s:%i.%i.%i\n",$1,$2,$3,$4)}' | \
column -t -s : | \
tr " " -

exit 0
