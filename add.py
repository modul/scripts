#!/usr/bin/env python
#
# add.py
#
# a short way to add lines to files lying
# under a configurable base directory.
# The base directory maybe specified using
# the environment variable ADDPY_BASEDIR.
# It defaults to ~/lists.
# Default file extensions can be specified
# with ADDPY_EXTENSIONS, a list of space
# seperated strings.
#
# Usage: add.py FILE [text...]
# Appends `text...` to FILE.
# If text is omitted, the scripts tries
# to open $EDITOR.
# FILE may be an absolute or relative 
# path or must be found in $ADDPY_BASEDIR.
# Each of $ADDPY_EXTENSIONS will be tried
# if the file extension is omitted. At 
# least '.txt' is tried as an extension.
# Files without extensions are found 
# without it, of course.
#
#  author: Remo Giermann
# created: 2010/6/2
#

import os, os.path
import sys
from string import join

editor = os.getenv("EDITOR")

basedir = os.getenv("ADDPY_BASEDIR") \
or "%s/doc/lists" % (os.getenv("HOME"))

extensions = os.getenv("ADDPY_EXTENSIONS") \
or "txt"

extensions = extensions.split()

def usage():

  print """
Usage: add.py FILE [text...]
Appends `text...` to FILE.
If text is omitted, the scripts tries
to open $EDITOR.
FILE may be an absolute or relative 
path or must be found in $ADDPY_BASEDIR.
Each of $ADDPY_EXTENSIONS will be tried
if the file extension is omitted. At 
least '.txt' is tried as an extension.
Files without extensions are found 
without it, of course.
"""

def locate(path):
  if os.path.isfile(path):
    return path
  if os.path.isfile(os.path.join(basedir, path)):
    return os.path.join(basedir, path)
  
  for ext in extensions:
    if os.path.isfile(path+'.'+ext):
      return path+'.'+ext
    if os.path.isfile(os.path.join(basedir, path+'.'+ext)):
      return os.path.join(basedir, path+'.'+ext)

  return None

argv = sys.argv
argc = len(argv)

if argc <= 1:
  usage()
else:
  filename = argv[1]
  path = locate(filename)
  if path is None:
    print "File %s could not be located." % (filename)
    sys.exit(1)
  
  if argc == 2:
    if editor is None:
      print "$EDITOR not defined."
      sys.exit(1)
    else:
      try:
        os.system(join([editor, path]))
      except:
        print "Could not launch $EDITOR."
        sys.exit(1)
      else:
        sys.exit(0)
  else:
    text = join(argv[2:])
    try:
      last = open(path, 'r').read()[-1]
      fp = open(path, 'a')
      if last != '\n':
        fp.write('\n')
      fp.write(text+'\n')
    except:
      print "Could not open file, permissions?"
      sys.exit(1)
    else:
      sys.exit(0)
