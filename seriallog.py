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

__version__ = "0.2"

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

def formatter(flist=[], sep="|"):
	''' Build a function that prepends some info strings to a string.
	Strings to be prepended are retrieved by calling functions in flist.
	'''
	def pieces(line):
		for f in flist:
			if callable(f):
				yield f()
		yield sep
		yield line

	def _formatter(line):
		return ' '.join(pieces(line))
	return _formatter


parser = ArgumentParser(description="Continuously read serial data", usage="%(prog)s [options] device")

parser.add_argument("device", help="serial device to open")

parser.add_argument("-v", "--version", action="version", version="%(prog)s "+__version__)
parser.add_argument("-q", "--quiet", action="store_true", help="don't print to stdout")
parser.add_argument("--interval", metavar="SEC", default=0.5, type=float, help="set read interval/timeout (0.5)")
parser.add_argument("--baudrate", metavar="BAUD", default=115200, type=int, help="set baudrate (115200)")
parser.add_argument("--logfile", metavar="FILE", type=FileType(mode="w"), help="write output to logfile")

group = parser.add_argument_group(title="Timestamps")
group.add_argument("--date", action="append_const", dest="timestamps", const=mk_date("%Y/%m/%d %H:%M:%S"), help="prepend time and date", default=None)
group.add_argument("--timestamp", action="append_const", dest="timestamps", const=mk_tstamp(), help="prepend timestamp", default=None)
group.add_argument("--seconds", action="append_const", dest="timestamps", const=mk_seconds(time.time()), help="prepend seconds since start", default=None)

group = parser.add_argument_group(title="Sending")
group.add_argument("--send", metavar="CMD", nargs="+", help="send serial commands, then read")
group.add_argument("--eol", default="lf", choices=["lf", "crlf", "cr"], help="choose end of line characters")

args = parser.parse_args()
eol = args.eol.replace("lf", "\n").replace("cr", "\r")

try:
	port = serial.Serial(args.device, args.baudrate, timeout=args.interval)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)
else:
	print "opened %s with %i Bps, %.1fs interval" % (args.device, args.baudrate, args.interval)
	if args.logfile:
		print "opened %s for logging" % (args.logfile.name)

fmt = formatter(args.timestamps)

try:
	while 1:
		if args.send:
			for cmd in args.send:
				port.write(cmd+eol)

		incoming = port.readlines()
		if not incoming:
			continue

		for line in incoming:
			buf = fmt(line)

			if not args.quiet:
				print buf,

			if args.logfile:
				print >> args.logfile, buf,
				args.logfile.flush()

except KeyboardInterrupt:
	sys.exit(0)
