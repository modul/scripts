#!/usr/bin/env python
# -*- coding: utf8 -*-
# 
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mo@liberejo.de> wrote this file. As long as you retain this notice you can
# do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
# 
# This script attaches a license or other informative header to a file.
#
# attach.py [options] files
# attach.py --help
#
# author: Remo Giermann
# created: 2012/05/15
#

__version__ = "0.1"

import sys
from time import strftime
from re import search
from shutil import copy
from itertools import count
from argparse import ArgumentParser

headers = {'none': ''}

headers['beer'] = """
----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
{mail} wrote this file. As long as you retain this notice you can
do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return - {author}.
----------------------------------------------------------------------------

"""

headers['copyright'] = """
Copyright (c) {year} {author} {mail}

"""

headers['waive'] = """
The author of this work hereby waives all claim of copyright (economic and moral)
in this work and immediately places it in the public domain. It may be used, 
distributed, distorted or destroyed in any manner whatsoever without further
attribution or notice to the creator - {author} {mail}, {year}

"""

headers['isc'] = """
Copyright (c) {year}, {author} {mail}

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH 
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND 
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""

headers['bsd2'] = """
Copyright (c) {year}, {author} {mail}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

    1. Redistributions of source code must retain the above copyright notice,
	   this list of conditions and the following disclaimer. 
    2. Redistributions in binary form must reproduce the above copyright notice,
	   this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

headers['mit'] = """
Copyright (C) {year} {author} {mail} 

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

	The above copyright notice and this permission notice shall be included
	in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

headers['wtfpl'] = """
         DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                 Version 2, December 2004

Copyright (C) {year} {author} {mail}

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.

         DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

0. You just DO WHAT THE FUCK YOU WANT TO.

"""

headers['reversed'] = """
All rights reversed.
{year} {author} {mail}

"""

def commentblock(text, s):
	if s == "none":
		return text
	comment = lambda s: '\n'.join(map(lambda x: s+x, text.splitlines()))
	if s == '"""' or s == "'''":
		return s+'\n'+comment('')+'\n'+s
	elif s == "/*":
		return s+'\n'+comment(' * ')+'\n'+' */'
	else:
		if not s.endswith(' '): s += ' '
		return comment(s)

def getheader(name):
	if name in headers:
		return headers[name]
	else:
		try:
			if name == '-':
				return '\n'+''.join(sys.stdin.readlines())+'\n'
			else:
				with open(name) as fp:
					return ''.join(fp.readlines())
		except IOError as msg:
			print "header:", msg
			return None
	return ''

def getlines(filename):
	try:
		with open(filename) as fp:
			return fp.readlines()
	except IOError as msg:
		print "original:", msg
		return None
	return []


if __name__ == "__main__":
	
	parser = ArgumentParser(\
			description="Attaches a header with license or other information to files. \
			Interpreter and file encoding lines at the beginning of a file will be left intact. ", \
			epilog="Available license headers: "+", ".join(headers.keys()) + ". \
			Supported commenting styles: /*, \"\"\", ''' or any single-line type like e.g. #, // or ;.")

	parser.add_argument("filenames", nargs="+", help="files to patch")
	parser.add_argument("-v", "--version", action="version", version="%(prog)s "+__version__)
	parser.add_argument("-f", "--force", action="store_true")
	parser.add_argument("-n", "--dry-run", action="store_true")
	parser.add_argument("--header", default="isc", help="choose a header from the list or a file, the default is 'isc'")
	parser.add_argument("--comment", default='#', help="set type of comment block or 'none'")
	parser.add_argument("--backup", action="store_true", help="make a backup copy of the original file")

	group = parser.add_argument_group(\
			title="Template Arguments", \
			description="All of these can be used in a header template like '{author}'.\
			If some argument is not present, it is replaced by an empty string.")
	group.add_argument("-a", "--author", default='')
	group.add_argument("-m", "--mail", default='', help="(will be enclosed in '<>')")
	group.add_argument("-y", "--year", default=strftime("%Y"))

	args = parser.parse_args()

	patch = getheader(args.header)
	if patch is None:
		sys.exit(1)

	context = {'author': args.author or '', 
			   'mail': args.mail and "<{}>".format(args.mail) or '', 
			   'year': args.year or ''}

	patch = patch.format(**context)
	patch = commentblock(patch, args.comment)

	if args.dry_run:
		print patch
		sys.exit(0)

	for filename in args.filenames:
		idx = 0
		origlines = getlines(filename)

		if origlines is None:
			continue
	
		if len(origlines) > 0:
			for oline, i in zip(origlines[:10], count()):
				if len(oline) > 3 and oline in patch and not args.force:
					print "{}: line {} kind of matches, file seems to have this header already.".format(filename, i)
					sys.exit(1)

			if origlines[0].startswith("#!"): 
				skip = 1
			else:
				if search("coding[:=]", origlines[0]):
					skip = 1
				else: skip = 0
			if search("coding[:=]", origlines[1]):
				skip = 2

		origlines.insert(skip, patch+'\n\n')

		try:
			if args.backup:
				copy(filename, filename+'~')
				print "backed up", filename
			with open(filename, "w") as fp:
				fp.writelines(origlines))
		except IOError as msg:
			print msg
			continue
		else:
			print "patched", filename
