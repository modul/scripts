#!/usr/bin/env python
# 
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mo@liberejo.de> wrote this file. As long as you retain this notice you can
# do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
#
# Very simple serial terminal
#
# If serial data is present, prints it.
# Afterwards, in any case, waits for user input.
#
# terminal.py --help
#
# author: Remo Giermann
# created: 2012/02/26
#

import sys
import serial
import readline
from argparse import FileType, ArgumentParser
from textwrap import fill

__version__ = "0.2.1"

# convert bytestring to hex, bin or decimal:
hexwidth, binwidth, decwidth = 3, 9, 4 # number of digits + 1 space
hexs = lambda text: (len(text)*"{:02x} ").format(*bytearray(text))
bins = lambda text: (len(text)*"{:08b} ").format(*bytearray(text))
decs = lambda text: (len(text)*"{: 3d} ").format(*bytearray(text))

# build functions to do or do not format paragraphs:
fm_par = lambda conv, bwidth: lambda width: lambda text: fill(conv(text), bwidth*width)+'\n'
no_par = lambda: lambda width: lambda text: text

def factory(options, port):
	''' Build helper functions based on settings in 'options'. '''
	from time import strftime

	fmt = options.converter(options.width)

	if '%' in options.prompt:
		pstr = lambda: strftime(options.prompt)
	else:
		pstr = lambda: options.prompt
	
	if options.prompt_cmd:
		def prompt():
			port.write(options.prompt_cmd + options.eol)
			incoming = fmt(port.readline()).strip()
			return raw_input(incoming + pstr())
	else:
		prompt = lambda: raw_input(pstr())

	return prompt, fmt

#----------------------------------------------------------

parser = ArgumentParser()
parser.usage = "%(prog)s device [command, ...] [options]"
parser.description = "A dumb serial terminal"
parser.epilog = """This 'terminal' waits for user input, sends it and prints any replies.
To fetch possible responses without sending anything just hit return.
Use CTRL-D or CTRL-C to quit."""

parser.add_argument("device", help="serial device to open")
parser.add_argument("commands", nargs='*', help="send commands and exit after response")

parser.add_argument("-v", "--version", action="version", version="%(prog)s "+__version__)
parser.add_argument("-q", "--quiet", action="store_true", help="don't print responses to stdout")
parser.add_argument("--baudrate", metavar="BAUD", default=115200, type=int, help="set baudrate (115200)")
parser.add_argument("--timeout", metavar="SEC", default=0.5, type=float, help="set read timeout (0.5)")
parser.add_argument("--eol", default="lf", choices=["lf", "crlf", "cr"], help="choose end of line characters")
parser.add_argument("--logfile", metavar="FILE", type=FileType(mode="w"), help="log everything to FILE")

group = parser.add_argument_group("Format")
group.add_argument("--hex", dest="converter", action="store_const", const=fm_par(hexs, hexwidth), default=no_par())
group.add_argument("--binary", dest="converter", action="store_const", const=fm_par(bins, binwidth), default=no_par())
group.add_argument("--decimal", dest="converter", action="store_const", const=fm_par(decs, decwidth), default=no_par())
group.add_argument("--width", default=8, type=int, help="how much bytes to display in a line")

group = parser.add_argument_group("Prompt")
group.add_argument("--prompt", metavar="STR", default="> ", help="show STR as prompt; might include strftime-like formatting")
group.add_argument("--prompt-cmd", metavar="CMD", help="show response to CMD in every prompt")

args = parser.parse_args()
eol  = args.eol = args.eol.replace("lf", "\n").replace("cr", "\r")

try:
	port = serial.Serial(args.device, args.baudrate, timeout=args.timeout)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)

#----------------------------------------------------------

prompt, formatter = factory(args, port)

if args.commands:
	for cmd in args.commands:
		port.write(cmd+eol)

	incoming = ''.join(port.readlines())
	if incoming:
		incoming = formatter(incoming)
		if not args.quiet:
			print incoming,
		if args.logfile:
			print >>args.logfile, incoming,
			args.logfile.flush()
	sys.exit(0)

#----------------------------------------------------------

try:

	while 1:
		incoming = ''.join(port.readlines())
		if incoming:
			incoming = formatter(incoming)
			if not args.quiet:
				print incoming,
			if args.logfile:
				print >> args.logfile, "< "+incoming,
				args.logfile.flush()

		try:
			cmd = prompt()
			if cmd:
				port.write(cmd+eol)
				if args.logfile:
					print >> args.logfile, "> "+cmd
		except EOFError:
			break

except KeyboardInterrupt:
	pass

finally:
	print "Bye."
	sys.exit(0)
