#!/usr/bin/env python
#
# Very simple serial terminal
#
# If serial data is present, prints it.
# Afterwards, in any case, waits for user input.
# CTRL-C to quit,
# CTRL-D to (re-)read serial port.
#
# terminal.py DEVICE [BAUDRATE] [TIMEOUT]
#

import sys
import serial
import readline

argv = sys.argv
argc = len(argv)

baudrate = 115200
timeout = .5
device = ''

if argc > 1:
	device = argv[1]
	if argc > 2:
		baudrate = int(argv[2])
		if argc > 3:
			timeout = int(argv[3])
else:
	print "Usage: %s DEVICE [BAUDRATE] [TIMEOUT]" % argv[0]
	sys.exit(1)

try:
	port = serial.Serial(device, baudrate, timeout=timeout)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)

print "opened %s with %i Bps, %.1fs timeout" % (device, baudrate, timeout)
port.setWriteTimeout(10 * timeout)

try:
	while 1:
		incoming = port.readlines()
		if incoming:
			for line in incoming[:-1]:
				print line,
			prompt = incoming[-1]
		else:
			prompt = 'no data> '
		try:
			i = raw_input(prompt)
			if i:
				port.write(i+'\n')
		except EOFError:
			if not prompt.endswith('\n'):
				print
except KeyboardInterrupt:
	sys.exit(0)
