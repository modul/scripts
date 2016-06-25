#!/usr/bin/env python
#
# Sorts files per file extensions into subdirs.
#
# author: mo
# created: 03/2016
#
#

import sys
import random
import string
from os import walk, mkdir
from os.path import join, exists, splitext
from hashlib import md5
from time import localtime
from shutil import copy, move

def randstring(length, chars=string.ascii_lowercase+string.digits):
	return ''.join(random.choice(chars) for c in range(length))

def checkname(path, force=False):
	random.seed()
	def _check(path):
		if exists(path):
			appd = '_' + randstring(4)
			orig = path
			name, ext = splitext(path)
			path = name + appd + ext
			print "{} exists already, trying {}".format(orig, path)
			return _check(path)
		return path
	return _check(path)		

def sortbyext(srcdir, dstdir, num=512):
	folders = {}
	if not exists(dstdir):
		print "Creating destination directory", dstdir
		mkdir(dstdir)
	for root, dirs, files in walk(srcdir, topdown=False):
		for name in files:
			ext = splitext(name)[1][1:].upper() or '_'
			if ext not in folders:
				folders.update([([ext, 0])])
			current = folders[ext]
			folders[ext] += 1
			src = join(root, name)
			dst = join(dstdir, ext)
			if not exists(dst):
				mkdir(dst)
			dst = join(dst, str(current / num))
			if not exists(dst):
				mkdir(dst)			
			dst = checkname(join(dst, name), force=True)
			print "{} {:>6d}: {} -> {}".format(ext, current, src, dst)
			copy(src, dst)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage: {} SOURCE DEST [COUNT]".format(sys.argv[0])
		sys.exit(1)

	src = sys.argv[1]
	dst = sys.argv[2]
	try: 
		num = int(sys.argv[3])
	except:
		num = 512
	sortbyext(src, dst, num)
