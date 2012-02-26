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

argv = sys.argv
argc = len(argv)

baudrate = 115200
timeout = 1
device = ''
logfile = ''

if argc > 1:
	device = argv[1]
	if argc > 2:
		baudrate = int(argv[2])
		if argc > 3:
			logfile = argv[3]
else:
	print "Usage: %s DEVICE [BAUDRATE] [LOGFILE]" % argv[0]
	sys.exit(1)

try:
	port = serial.Serial(device, baudrate, timeout=timeout)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)

print "opened %s with %i Bps, %.1fs timeout" % (device, baudrate, timeout)
port.setWriteTimeout(10 * timeout)

try:
	log = open(logfile, 'w')
except IOError as msg:
	print msg
	log = None
else:
	print "opened %s for writing" % logfile

try:
	while 1:
		incoming = port.readlines()
		if incoming:
			for line in incoming:
				print line,
				if log:
					print >> log, line,
except KeyboardInterrupt:
	sys.exit(0)
