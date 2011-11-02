# makefile to use rsync to synchronize
# files to usb storrage
# specialized for use with my study files
#
# Remo Giermann
# 2010/02/02


RSYNC=rsync
RSYNCFLAGS=--delete -turv #preserve times, update only, recursivley, verbosely
SOURCE=~/doc/studium
DESTIN=/media/rgrm/

all: put


put:
	$(RSYNC) $(RSYNCFLAGS) $(SOURCE) $(DESTIN)
