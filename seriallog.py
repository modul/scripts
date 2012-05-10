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
from argparse import FileType, ArgumentParser

parser = ArgumentParser(description="Continously read serial data", usage="%(prog)s [options] device")
parser.add_argument("device", help="serial device to open")
parser.add_argument("--baudrate", "-b", default=115200, type=int, help="baudrate (bps) to set")
parser.add_argument("--logfile", "-l", metavar="FILE", type=FileType(mode="w"), help="file to log to")
parser.add_argument("--quiet", "-q", action="store_true", help="don't print to stdout")
parser.add_argument("--timeout", default=0.5, type=float, help="timeout for serial read/write")

args = parser.parse_args()

try:
	port = serial.Serial(args.device, args.baudrate, timeout=args.timeout)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)
else:
	print "opened %s with %i Bps, %.1fs timeout" % (args.device, args.baudrate, args.timeout)

if args.logfile:
	print "opened %s for writing" % (args.logfile.name)

try:
	while 1:
		incoming = port.readlines()
		if incoming:
			for line in incoming:
				if not args.quiet:
					print line,
				if args.logfile:
					print >> args.logfile, line,
except KeyboardInterrupt:
	sys.exit(0)
