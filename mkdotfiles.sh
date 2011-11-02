#!/bin/sh
#
# mkdotfiles.sh
#
# creates a gzipped tar-archive of your dotfiles (~/.*) some
# unnecessary cache directories excluded.
# 
# The script uses environment variables for configuration. 
# Change them on the command line to change source and destination
# patterns.
#
# $HOME - source of dotfiles (if unset or empty, defaults to ./)
# $HOSTNAME - name of the machine (if unset or empty, use output of 'hostname')
# $DESTINATION - destination path for the archive (if unset or empty, defaults to ./)
#
#  author: Remo Giermann
# created: 2010/6/1
# updated: 2011/6/7
#          2011/10/25
#

_source=${HOME:-.}
_destin=${DESTINATION:-.}; _destin=${_destin%/} # strip trailing slash

hostname=${HOSTNAME:-`hostname`}; hostname=${hostname%.*} # strip domain, if any
filename="$_destin/$hostname-dotfiles-`date +%Y%m%d-%HH%M`.tgz"

echo Source $_source/
echo Destination $filename

for i in `seq 1 5`; do echo -n .; sleep 1; done	

echo starting.; sleep 2

tar \
--exclude-caches-all \
--exclude-vcs \
--exclude '*[cC]ache*' \
--exclude 'tmp' \
--exclude '.tmp' \
--exclude '*thumbnails*' \
--exclude '.macromedia' \
--exclude '.cpan' \
--exclude '.marble/data' \
--exclude '.mozilla/firefox/Crash Reports' \
-cvpzf $filename $_source/.[a-zA-Z0-9]*

echo
echo finished.
