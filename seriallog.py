#!/usr/bin/env python
#
# Very simple serial logger
#
# Continuously reads and prints serial data
# and optionally writes it to a logfile.
#
# seriallog.py DEVICE [BAUDRATE] [LOGFILE]
#

import sys
import serial
from time import sleep
from argparse import FileType, ArgumentParser

TIMEOUT = 0.5

parser = ArgumentParser(description="Continously read serial data", usage="%(prog)s [options] device")
parser.add_argument("device", help="serial device to open")
parser.add_argument("--quiet", "-q", action="store_true", help="don't print to stdout")
parser.add_argument("--baudrate", "-b", default=115200, type=int, help="baudrate (bps) to set")
parser.add_argument("--logfile", "-l", metavar="FILE", type=FileType(mode="w"), help="file to log to")
parser.add_argument("--send", metavar="CMD", nargs="+", help="write serial commands, then read")
parser.add_argument("--wait", metavar="t", default=0, type=float, help="wait before reading")
parser.add_argument("--eol", default="lf", choices=["lf", "lfcr", "crlf", "cr"], help="which EOL to send")
parser.add_argument("--date", action="store_true", help="prepend time and date")
parser.add_argument("--timestamp", action="store_true", help="prepend timestamp")
parser.add_argument("--seconds", action="store_true", help="prepend seconds since start")

args = parser.parse_args()
args.eol.replace("lf", "\n")
args.eol.replace("cr", "\r")

try:
	port = serial.Serial(args.device, args.baudrate, timeout=TIMEOUT)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)
else:
	print "opened %s with %i Bps, %.1fs interval" % (args.device, args.baudrate, args.wait)

if args.logfile:
	print "opened %s for writing" % (args.logfile.name)

try:
	while 1:
		if args.send:
			for cmd in args.send:
				port.write(cmd+args.eol)

		if args.wait:
			sleep(args.wait)

		incoming = port.readlines()
		if incoming:
			for line in incoming:
				if not args.quiet:
					print line,
				if args.logfile:
					print >> args.logfile, line,
except KeyboardInterrupt:
	sys.exit(0)
