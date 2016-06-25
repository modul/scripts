#!/usr/bin/env python
# 
# winname.py - renames files in a directory, so that
# Windoze doesn't choke on "illegal characters".
#
# All rights reversed.
# 2012 Remo Giermann <mo@liberejo.de>
# 

import os, re

from sys import argv
from shutil import move

KILL = '\\:*?"><|'
REPLACE = ''
PATTERN = r'.*[{}].*'.format(KILL)

def match(name):
	return re.match(PATTERN, name)

def replace(src):
	dst = src
	for k in KILL:
		dst = dst.replace(k, REPLACE)
	return dst

def renamer(path):
	def rename(source):
		src = os.path.join(path, source)
		dst = os.path.join(path, replace(source))
		move(src, dst)
		return src, dst
	return rename

def recurse(directory):
	for dirpath, dirs, files in os.walk(directory):
		rename = renamer(dirpath)
		for f in filter(match, files):
			src, dst = rename(f)
			print src, "->", dst
		for d in filter(match, dirs):
			src, dst = rename(d)
			dirs[dirs.index(d)] = os.path.basename(dst)
			print src, "->", dst

if __name__ == "__main__":

	if len(argv) < 2:
		print argv[0], "DIRECTORY [REPLACEMENT]"
	else:
		if len(argv) == 3:
			REPLACE = argv[2]
		recurse(argv[1])
