#!/usr/bin/env python
# 
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mo@liberejo.de> wrote this file. As long as you retain this notice you can
# do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
#
# Very simple serial logger
#
# Continuously reads and prints serial data
# and optionally writes it to a logfile.
#
# seriallog.py --help
#
# author: Remo Giermann
# created: 2012/02/26
#

import sys
import serial
import time
from argparse import FileType, ArgumentParser

__version__ = "0.3.2"

hexs = lambda text: ' '.join("{:02x}".format(x) for x in bytearray(text))
bins = lambda text: ' '.join("{:08b}".format(x) for x in bytearray(text))
decs = lambda text: ' '.join("{: 3d}".format(x) for x in bytearray(text))

def mk_date(fmt):
	''' Return a wrapper for strftime(fmt) '''
	def date():
		return time.strftime(fmt)
	return date

def mk_tstamp():
	''' Return a wrapper for getting a timestamp-string '''
	def timestamp():
		return str(int(time.time()))
	return timestamp

def mk_seconds(start):
	''' Return a wrapper to get the str-formatted seconds since 'start' '''
	def seconds():
		return "{:6.2f}".format(time.time()-start)
	return seconds

def formatter(flist=[], conv=None, width=0, sep="| "):
	''' Build a function that prepends some info strings to a string,
	which is, if conv is one of hexs, decs or bins, first converted
	to a hex, decimal or binary dump.
	Strings to be prepended are retrieved by calling functions in flist and
	are separated from the base string using 'sep'.
	When width > 0, text is wrapped to 'width' characters per line or
	'width' number of bytes per line if conv is used.
	'''
	from textwrap import fill

	if flist:
		flist += [sep]

	if not callable(conv):
		chars = 1
		convert = lambda text: text
	else:
		chars = len(conv('\xff')) + 1
		convert = lambda text: conv(text)
	
	if width:
		def par(indent, text):
			return fill(text, width*chars + indent,
					subsequent_indent=' '*indent,
					replace_whitespace=False,
					drop_whitespace=False)
	else:
		def par(indent, text):
			return text

	def _formatter(line):
		prefix = ' '.join(callable(f) and f() or str(f) for f in flist)
		return par(len(prefix), prefix + convert(line))

	return _formatter


parser = ArgumentParser(description="Continuously read serial data", usage="%(prog)s [options] device")

parser.add_argument("device", help="serial device to open")

parser.add_argument("-v", "--version", action="version", version="%(prog)s "+__version__)
parser.add_argument("-q", "--quiet", action="store_true", help="don't print to stdout")
parser.add_argument("--interval", metavar="SEC", default=0.5, type=float, help="set read interval/timeout (0.5)")
parser.add_argument("--baudrate", metavar="BAUD", default=115200, type=int, help="set baudrate (115200)")
parser.add_argument("--logfile", metavar="FILE", type=FileType(mode="w"), help="write output to logfile")

group = parser.add_argument_group(title="Timestamps")
group.add_argument("--date", action="append_const", dest="timestamps", const=mk_date("%Y/%m/%d %H:%M:%S"), help="prepend time and date", default=[])
group.add_argument("--timestamp", action="append_const", dest="timestamps", const=mk_tstamp(), help="prepend timestamp", default=[])
group.add_argument("--seconds", action="append_const", dest="timestamps", const=mk_seconds(time.time()), help="prepend seconds since start", default=[])

group = parser.add_argument_group("Format")
group.add_argument("--width", default=70, type=int, help="number of characters/bytes per line")
group.add_argument("--hex", dest="converter", action="store_const", const=hexs, default=None, help="display responses as hex")
group.add_argument("--binary", dest="converter", action="store_const", const=bins, default=None, help="display responses as decimal")
group.add_argument("--decimal", dest="converter", action="store_const", const=decs, default=None, help="display responses as binary")

group = parser.add_argument_group(title="Sending")
group.add_argument("--send", metavar="CMD", nargs="+", help="send serial commands, then read")
group.add_argument("--eol", default="lf", choices=["lf", "crlf", "cr", "lfcr", "none"], help="choose end of line characters (lf)")

args = parser.parse_args()
eol = args.eol.replace("lf", "\n").replace("cr", "\r").replace("none", "")

try:
	port = serial.Serial(args.device, args.baudrate, timeout=args.interval)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)
else:
	print "opened %s with %i Bps, %.1fs interval" % (args.device, args.baudrate, args.interval)
	if args.logfile:
		print "opened %s for logging" % (args.logfile.name)

fmt = formatter(args.timestamps, args.converter, args.width)

try:
	while 1:
		if args.send:
			for cmd in args.send:
				print >> port, cmd+eol,

		incoming = port.readlines()
		if not incoming:
			continue

		for line in incoming:
			buf = fmt(line).strip()

			if not args.quiet:
				print buf

			if args.logfile:
				print >> args.logfile, buf
				args.logfile.flush()

except KeyboardInterrupt:
	sys.exit(0)
