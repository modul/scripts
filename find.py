# -*- coding: utf8 -*-
#
# Finding files with python
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mo@liberejo.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
#
# author:  Remo Giermann
# created: 2011/04
# updated: 2012/05/15
#

import os
import sys
import time
from re import match

def check_time(path, days):
	"""
	Checks creation and modification time of 'path' and returns
	True if it was modified or created in the last 'days' days
	False otherwise.
	"""
	stats = os.stat(path)
	mtime = stats.st_mtime
	ctime = stats.st_ctime
	
	now = time.time()
	then = now - days*24*3600	
	return mtime > then or ctime > then

def find(directory, name='', days=0, hook=None):
	"""
	Find files in 'directory' (recursively). 'name' might be a regular
	expression to match against the filename (not the path). If 'days' is not
	zero, match only files modified in the last days. If 'hook' is callable,
	then it will be called on any file found with the filename as an argument.
	Otherwise, if 'hook' is True, results get printed.

	>>> find("./", name=r"find.pyc?")
	./find.pyc
	./find.py
	"""
	if callable(hook):
		call = hook
	elif hook is True:
		def call(x):
			print x
	else:
		def call(x):
			pass
	
	for dirpath, dirs, files in os.walk(directory):
		for f in files: # match file names
			path = os.path.join(dirpath, f)
			if match(name, f) is not None:
				if days == 0 or check_time(path, days) is True:
					call(path)
		for d in dirs: # match dir names
			path = os.path.join(dirpath, d)
			if match(name, d) is not None:
				if days == 0 or check_time(path, days) is True:
					call(path)
			if days > 0 and check_time(path, days) is False: #remove unmodified directories
				dirs.remove(d)

#------------------------------------------------------------------------------
if __name__ == '__main__': 
	from sys import argv, exit
	from timeit import Timer
	import commands

	def gnufind(directory, mtime):
		findstring = 'find %s -mtime -%i -and \( -iname "*.mp3" -or -iname "*.ogg" -or -iname "*.flac" \)'
		commands.getoutput(findstring % (directory, mtime))
	
	usage = """
to compare gnufind and pytfind run
{0} COUNT DIRECTORY DAYS

Starting both functions to look for  music files modified
within the last DAYS in DIRECTORY.
This is run COUNT times and the timing results are printed.
""".format(argv[0])

	if len(argv) < 4:
		print usage
		exit(1)

	count = int(argv[1])
	path = argv[2]
	days = int(argv[3])
	print "looking in {path} for music from the last {days} days - repeating {c} times...".format(path=path, days=days, c=count)

	gnu = Timer("gnufind(path, days)", "from __main__ import gnufind, path, days")
	pyt = Timer("find(name=r'.*\.(ogg|flac|mp3)', directory=path, days=days)", "from __main__ import find, path, days")
	tpyt = pyt.repeat(number=1, repeat=count)
	tgnu = gnu.repeat(number=1, repeat=count)
	
	print "gnufind: {min:0<6.4}, {avg:0<6.4}, {max:0<6.4}".format(min=min(tgnu), max=max(tgnu), avg=sum(tgnu)/count)
	print "pytfind: {min:0<6.4}, {avg:0<6.4}, {max:0<6.4}".format(min=min(tpyt), max=max(tpyt), avg=sum(tpyt)/count)
