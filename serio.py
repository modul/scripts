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

parser = ArgumentParser(description="Sends a comand to a serial terminal and prints the response.", usage="%(prog)s [options] device command")
parser.add_argument("device", help="serial device to open")
parser.add_argument("command", help="command to send")
parser.add_argument("--baudrate", metavar="BAUD", default=115200, type=int, help="set baudrate (115200)")
parser.add_argument("--eol", default="lf", choices=["lf", "crlf", "cr", "lfcr", "none"], help="end of line characters (lf)")

args = parser.parse_args()
eol = args.eol.replace("lf", "\n").replace("cr", "\r").replace("none", "")

port = Serial(args.device, args.baudrate, timeout=1)
print >>port, args.command + eol,
for line in port.readlines():
	print line.strip()
