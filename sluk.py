#!/usr/bin/env python
# 
# All rights reversed.
# 2012 Remo Giermann <mo@liberejo.de>
# 

#
# Split text into fields, take one field as a
# key and summarize lines with that same key like:
#
# very useful with log files, e.g.:
# > git log --date=short --pretty="format:%ad %s" | sluk.py 
# will produce output like:
#
# 2012-11-24:
# Commit message
# Commit message
# ...
#
# 2012-11-25:
# Commit message
# ...

from argparse import ArgumentParser, FileType
from sys import stdin, argv

def sorter(direction=0, **kwargs):
	if direction == 1:
		return lambda it: sorted(it, **kwargs)
	elif direction == -1:
		return lambda it: sorted(it, reverse=True, **kwargs)
	else:
		return lambda it: it

parser = ArgumentParser(description="Summarize lines using key fields")
parser.add_argument("-k", type=int, dest="key", default=0, help="index of field to use as key")
parser.add_argument("-d", type=str, dest="delim", default=' ', help="field delimiter")
parser.add_argument("-i", type=str, dest="inden", default='', help="indention character(s)")
parser.add_argument("-s", type=str, dest="keysp", default=':', help="key separator")
parser.add_argument("-r", action="store_const", dest="sort", default=sorter(1), const=sorter(-1), help="reverse sort keys")
parser.add_argument("-n", action="store_const", dest="sort", default=sorter(1), const=sorter( 0), help="do not sort keys")
args = parser.parse_args(argv[1:])

data = {}
for line in stdin:
	fields = line.split(args.delim)
	key, text = fields.pop(args.key).strip(), args.delim.join(fields).strip()
	data.setdefault(key, []).append(text.strip())

for key in args.sort(data.keys()):
	print key + args.keysp
	for text in data[key]:
		print args.inden + text
	print
