#!/usr/bin/env python
#
# Very simple serial logger
#
# Continuously reads and prints serial data
# and optionally writes it to a logfile.
#
# seriallog.py --help
#
# author: Remo Giermann
# created: 2011
#

import sys
import serial
import time
from argparse import FileType, ArgumentParser

parser = ArgumentParser(description="Continuously read serial data", usage="%(prog)s [options] device")
parser.add_argument("device", help="serial device to open")
parser.add_argument("-q", "--quiet", action="store_true", help="don't print to stdout")
parser.add_argument("--interval", metavar="SEC", default=0.5, type=float, help="set read interval/timeout")
parser.add_argument("--baudrate", metavar="BAUD", default=115200, type=int, help="set baudrate, default is 115200")
parser.add_argument("--logfile", metavar="FILE", type=FileType(mode="w"), help="write to logfile")

group = parser.add_argument_group(title="Timestamps")
group.add_argument("--date", action="store_true", help="prepend time and date")
group.add_argument("--timestamp", action="store_true", help="prepend timestamp")
group.add_argument("--seconds", action="store_true", help="prepend seconds since start")

group = parser.add_argument_group(title="Sending")
group.add_argument("--send", metavar="CMD", nargs="+", help="write serial commands, then read")
group.add_argument("--eol", default="lf", choices=["lf", "lfcr", "crlf", "cr"])

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


fmt  = args.timestamp and "{timestamp} " or ""
fmt += args.date      and "{date} " or ""
fmt += args.seconds   and "{sec:.2f} " or ""
fmt += "{line}"

try:
	tstart = time.time()
	while 1:
		if args.send:
			for cmd in args.send:
				port.write(cmd+eol)

		incoming = port.readlines()
		if not incoming:
			continue

		for line in incoming:
			buf = fmt.format(line=line, \
					timestamp=int(time.time()), \
					date=time.strftime("%Y/%m/%d %H:%M:%S"), \
					sec=time.time()-tstart)

			if not args.quiet:
				print buf,

			if args.logfile:
				print >> args.logfile, buf,

except KeyboardInterrupt:
	sys.exit(0)
