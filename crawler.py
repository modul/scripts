#!/usr/bin/env python
#
# Crawls a webpage for links to files with certain extensions and 
# tries to retrieve these files.
#
# Should match absolute urls anywhere in the text as well as absolute and relative urls in attributes
#
# created: 2011/05/02
# author: Remo Giermann

import os
import sys
import argparse
import re
import urllib
import urllib2

from urlparse import urlsplit

__version__ = "0.0.1"

p_absolute  = r'http://[^"\' ]+\.{extension}'           # matches absolute urls anywhere
p_attribute = r'[=]["\']?[^"\' ]+\.{extension}["\']?'  # matches any url following an equal-sign (and enclosed by optional " or ')

extensions = {
 'docs'  : ['pdf', 'ps', 'doc'],
 'video': ['mpg', 'avi', 'mp4', 'mkv', 'flv', 'mov', 'wmv'],
 'audio': ['ogg', 'flac', 'mp3', 'wav', 'aif', 'wma'],
 'images': ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff']
}

# Convert bytes to human-readable format 
def convertsize(b):
   if b > 2**20:
	   size = "{:.2f}M".format(float(b)/2**20)
   elif b > 2**10:
	   size = "{:.2f}K".format(float(b)/2**10)
   else:
	   size = "{}B".format(float(b))
   return size

# Progress 'bar'
def print_progress(blocks, blocksize, size):
	totalblocks = float(size)/blocksize
	percentage  = float(blocks)/totalblocks*100
	print "  {perc:.0f}% of {size} ({bl}/{total:.0f} blocks)\r".format(size=convertsize(size), perc=percentage, bl=blocks, total=totalblocks),

# Setup argument parser
parser = argparse.ArgumentParser(version=__version__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.description = "Search a webpage for links with certain file extensions and tries to retrieve these files."
parser.epilog = "\nmatching file extensions:\n" + '\n'.join(['  {name}: {exts}'.format(name=k, exts=', '.join(v)) for k, v in extensions.items()])

parser.add_argument('-l', '--list', help='only list matched links, don\'t retrieve', dest='listonly', action='store_true')
parser.add_argument('-q', '--quiet', help='print less', action='store_false', dest='verbose')
parser.add_argument('--ignore', help='ignore this mimetype (default: text/)', dest='ignoretypes', action='append', default=['text/'], metavar='MIME')
parser.add_argument('exts', help='file extensions to look for (any extension or one of docs, audio, video, images)', metavar='TYPE')
parser.add_argument('URL', help='where to crawl')

args = parser.parse_args()

# Startup
print >> sys.stderr, "crawling {tp} from {url}\n".format(tp=args.exts, url=args.URL)

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
urllib2.install_opener(opener)

fd = opener.open(args.URL)
# we may need a cookie, do it again
fd = opener.open(args.URL)
page = fd.read()
fd.close()

# Get file extensions
if args.exts not in extensions.keys():
	exts = [args.exts]
else: 
	exts = extensions[args.exts]

# Look for absolute links
pattern = re.compile(r'|'.join([p_absolute.format(extension=x) for x in exts]))
matches = pattern.findall(page)

# Look for links in attributes too
pattern = re.compile(r'|'.join([p_attribute.format(extension=x) for x in exts]))
matches.extend(pattern.findall(page))

# Quit on zero matches
if len(matches) == 0:
	print >> sys.stderr, "No matches found."
	sys.exit(0)

# Process matches
links = []	
url = urlsplit(args.URL)
domain  = url.scheme+'://'+url.netloc
path = os.path.dirname(url.path)[1:]

for match in set(matches):
	link = re.sub('[\'"=]', '', match)
	if link.startswith('/'):                 # Links like /path/to/file
		link = os.path.join(domain, link[1:])    # Rewritten to http://domain/path/to/file
	if not link.startswith('http://'):       # Links like ../file or directory/file
		link = os.path.join(domain, path, link) # Rewritten to http://domain/basepath/../file or http://domain/basepath/directory/file resp.

	try:
		urlinfo = opener.open(link).info()
	except (urllib2.HTTPError, urllib2.URLError) as reason:
		# leave out dead links (or funny matches)
		if args.verbose is True:
			print >> sys.stderr, "ignoring ({reason}) {url}".format(url=link, reason=reason)
	else:
		ct = ''
		cl = 0
		if urlinfo.has_key('content-length'):
			cl = int(urlinfo['content-length'])
		if urlinfo.has_key('content-type'):
			ct = urlinfo['content-type'].split(';')[0]
			# check if we should ignore this content-type:
			if filter(lambda t: t in ct, args.ignoretypes):	
				if args.verbose is True:
					if len(link) > 50:
						link = '...'+link[-(47):]
					print >> sys.stderr, "ignoring ({reason}) {url}".format(url=link, reason='Mimetype')
				continue
		# everything passed, now add this wonderful link!
		links.append(link)

		if args.listonly is True:
			print link
		else:
			if len(link) > 50:
				link = '...'+link[-(67):]
			print "[{n: >3}] {content: <30} {size: >8} {link}".format(n=len(links)-1, link=link, content=ct, size=convertsize(cl))


if len(links) == 0:
	print >> sys.stderr, "No links found."
	sys.exit(0)

if args.listonly is True:
	sys.exit(0)	

# Ask for link(s) to retrieve, not error proof!!
ans = raw_input("Choice (number, range, list, * or [q]): ")
if '-' in ans:
	a = map(int, ans.split('-'))
	choices = range(a[0], a[1]+1)
elif ',' in ans:
	choices = map(int, ans.split(','))
elif ans == '*':
	choices = range(len(links))
elif ans.isdigit():
	choices = [int(ans)]
elif ans in ('', 'q'):
	sys.exit(0)
else:
	print "Bad choice."
	sys.exit(1)

# Iterate over choices and try to retrieve the files
ans = raw_input("New name (multiple files will be indexed): ")
for i in choices:
	if i < 0 or i >= len(links):
		print "Bad choice: ", i
	else:
		filename = os.path.basename(links[i])
		extension = filename[-3:]
		if ans not in ('', ' '):
			if len(choices) > 1:
				filename = "{name}-{idx}.{ext}".format(name=ans, idx=choices.index(i), ext=extension)
			else:
				filename = "{name}.{ext}".format(name=ans, ext=extension)

		print "Retrieving", filename
		try:
			f, i = urllib.urlretrieve(links[i], filename=filename, reporthook=print_progress)
		except urllib.ContentTooShortError, msg:
			print
			print "\n  :( download interrupted?"
			print msg
		else:
			print "\n  :) done!"
