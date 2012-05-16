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

parser = ArgumentParser(description="Continuously read serial data", usage="%(prog)s [options] device")

parser.add_argument("device", help="serial device to open")

parser.add_argument("-v", "--version", action="version", version="%(prog)s "+__version__)
parser.add_argument("-q", "--quiet", action="store_true", help="don't print to stdout")
parser.add_argument("--interval", metavar="SEC", default=0.5, type=float, help="set read interval/timeout (0.5)")
parser.add_argument("--baudrate", metavar="BAUD", default=115200, type=int, help="set baudrate (115200)")
parser.add_argument("--logfile", metavar="FILE", type=FileType(mode="w"), help="write output to logfile")

group = parser.add_argument_group(title="Timestamps")
group.add_argument("--date", action="store_true", help="prepend time and date")
group.add_argument("--timestamp", action="store_true", help="prepend timestamp")
group.add_argument("--seconds", action="store_true", help="prepend seconds since start")

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


fmt  = args.timestamp and "{timestamp} " or ""
fmt += args.date      and "{date} " or ""
fmt += args.seconds   and "{sec: 6.2f} " or ""
fmt += fmt and "| {line}" or "{line}"

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
				args.logfile.flush()

except KeyboardInterrupt:
	sys.exit(0)
