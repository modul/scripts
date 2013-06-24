#!/usr/bin/env python
# 
# All rights reversed.
# 2013 Remo Giermann <mo@liberejo.de>
# 
# This script just sends a command to a serial terminal
# and prints its response.
#

from serial import Serial
from argparse import ArgumentParser

hexs = lambda text: ' '.join("{:02x}".format(x) for x in bytearray(text))
bins = lambda text: ' '.join("{:08b}".format(x) for x in bytearray(text))
decs = lambda text: ' '.join("{: 3d}".format(x) for x in bytearray(text))

parser = ArgumentParser(description="Sends a comand to a serial terminal and prints the response.", usage="%(prog)s [options] device command")
parser.add_argument("device", help="serial device to open")
parser.add_argument("command", help="command to send")
parser.add_argument("--baudrate", metavar="BAUD", default=115200, type=int, help="set baudrate (115200)")
parser.add_argument("--eol", default="lf", choices=["lf", "crlf", "cr", "lfcr", "none"], help="end of line characters (lf)")
parser.add_argument("--hex", dest="converter", action="store_const", const=hexs, default=None, help="display responses as hex")
parser.add_argument("--binary", dest="converter", action="store_const", const=bins, default=None, help="display responses as binary")
parser.add_argument("--decimal", dest="converter", action="store_const", const=decs, default=None, help="display responses as decimal")

args = parser.parse_args()
eol = args.eol.replace("lf", "\n").replace("cr", "\r").replace("none", "")

port = Serial(args.device, args.baudrate, timeout=1)
print >>port, args.command + eol,
for line in port.readlines():
	if args.converter: print args.converter(line)
	else: 	print line.strip()
