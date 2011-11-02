#!/usr/bin/env python
#
# This script requests a version description from git using git describe
# and saves it to a text file in your project's directory and also
# as a python pickle file. The latter holds version and revision as a dict.
# 
# author: Remo Giermann
# created: 2011/04/14
#
import sys
import os
import pickle
import commands

ABBREV = 4
VERSIONFILE = 'version'
VERSIONPIKL =  VERSIONFILE + '.pkl'
descr = commands.getoutput('git describe --abbrev=%i' % ABBREV)

if not descr.startswith('v'):
	print >> sys.stderr, "Could not get a version description from git."
	print >> sys.stderr, "Message was:", descr
	print >> sys.stderr, "If everything _should_ be ok but isn't, remember that you have to create"
	print >> sys.stderr, "_annotated_ tags named after the version number, starting with 'v',"
	print >> sys.stderr, "or use a more tolerant script."
	sys.exit(1)

version, revision = (0, 0)
v = descr.split('-')
if len(v) == 3:
	version, revision, commit = v
versioninfo = {'version': version, 'revision': revision}

if os.path.isfile(VERSIONPIKL):
	with open(VERSIONPIKL) as fd:
		old = pickle.load(fd)
else:
	old = {}

if old == versioninfo:
	print >> sys.stderr, "Not updating version."
else:
	print >> sys.stderr, "Updating version."
	with open(VERSIONFILE, 'w') as fd:
		fd.write(descr+'\n')
	with open(VERSIONPIKL, 'w') as fd:
		pickle.dump(versioninfo, fd)
