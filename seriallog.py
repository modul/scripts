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
import time
from argparse import FileType, ArgumentParser

TIMEOUT = 0.5

parser = ArgumentParser(description="Continuously read serial data", usage="%(prog)s [options] device")
parser.add_argument("device", help="serial device to open")
parser.add_argument("-q", "--quiet", action="store_true", help="don't print to stdout")
parser.add_argument("--baudrate", metavar="BAUD", default=115200, type=int, help="set baudrate, default is 115200")
parser.add_argument("--logfile", metavar="FILE", type=FileType(mode="w"), help="write to logfile")
parser.add_argument("--wait", metavar="t", default=0, type=float, help="wait some time before reading")

group = parser.add_argument_group(title="Timestamps")
group = group.add_mutually_exclusive_group()
group.add_argument("--date", action="store_true", help="prepend time and date")
group.add_argument("--timestamp", action="store_true", help="prepend timestamp")
group.add_argument("--seconds", action="store_true", help="prepend seconds since start")

group = parser.add_argument_group(title="Sending")
group.add_argument("--send", metavar="CMD", nargs="+", help="write serial commands, then read")
group.add_argument("--eol", default="lf", choices=["lf", "lfcr", "crlf", "cr"])

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

tstart = time.time()

fmt = "{line}"
fmt = args.timestamp and "{timestamp} " + fmt or fmt
fmt = args.date      and "{date} " + fmt or fmt
fmt = args.seconds   and "{sec:.2f} " + fmt or fmt

try:
	while 1:
		if args.send:
			for cmd in args.send:
				port.write(cmd+args.eol)

		if args.wait:
			time.sleep(args.wait)

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
