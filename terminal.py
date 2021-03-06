#!/usr/bin/env python
# 
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mo@liberejo.de> wrote this file. As long as you retain this notice you can
# do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
#
# Simple serial terminal - with some practical options and features.
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

__version__ = "0.2.4"

### Converters for hex, binary or decimal dumps ###

hexs = lambda text: ' '.join("{:02x}".format(x) for x in bytearray(text))
bins = lambda text: ' '.join("{:08b}".format(x) for x in bytearray(text))
decs = lambda text: ' '.join("{: 3d}".format(x) for x in bytearray(text))

### Build helper functions based on options ###

def formatter(converter=None, width=0):
	''' Build a string formatting function.
	If converter is one of hexs, bins or decs, width is the number of bytes
	to put on one line. If converter is None, given text is returned
	untouched. 
	'''
	from textwrap import fill
	if converter:
		digits = len(converter("\xff"))
		chars = width * (digits + 1)
		def fmt(text):
			return fill(converter(text), chars) + '\n'
	else:
		def fmt(text):
			return text
	return fmt

def prompter(promptstr, cmd=None, port=None):
	''' Build a function that asks for input, printing a prompt based on 
	arguments. 
	promptstr might include strftime-like patterns. If cmd and port is given,
	cmd is sent through port and the response gets prepended to each prompt.
	'''
	from time import strftime
	if '%' in promptstr:
		pstr = lambda: strftime(promptstr)
	else:
		pstr = lambda: promptstr
	
	if cmd and port:
		def prompt():
			port.write(cmd)
			incoming = fmt(port.readline()).strip()
			return raw_input(incoming + pstr())
	else:
		prompt = lambda: raw_input(pstr())
	return prompt

### Setup commandline arguments ###

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
parser.add_argument("--logfile", metavar="FILE", type=FileType(mode="w"), help="log everything to FILE")
parser.add_argument("--eol", default="lf", choices=["lf", "crlf", "cr", "lfcr", "none"], help="choose end of line characters (lf)")

group = parser.add_argument_group("Format")
group.add_argument("--hex", dest="converter", action="store_const", const=hexs, default=None)
group.add_argument("--binary", dest="converter", action="store_const", const=bins, default=None)
group.add_argument("--decimal", dest="converter", action="store_const", const=decs, default=None)
group.add_argument("--width", default=8, type=int, help="number of bytes per line")

group = parser.add_argument_group("Prompt")
group.add_argument("--prompt", metavar="STR", default="> ", help="show STR as prompt; might include strftime-like formatting")
group.add_argument("--prompt-cmd", metavar="CMD", help="show response to CMD in every prompt")


### Parse commandline and setup environment ###

args = parser.parse_args()
args.eol = args.eol.replace("lf", "\n").replace("cr", "\r").replace("none", "")

try:
	port = serial.Serial(args.device, args.baudrate, timeout=args.timeout)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)

cmd = args.prompt_cmd and args.prompt_cmd+args.eol or None

fmt = formatter(args.converter, args.width)
prompt = prompter(args.prompt, cmd, port)

### Fire and forget commands given on commandline ###

if args.commands:
	for cmd in args.commands:
		print >> port, cmd + args.eol,

	incoming = ''.join(port.readlines())
	if incoming:
		if not args.quiet:
			print fmt(incoming),
		if args.logfile:
			print >> args.logfile, fmt(incoming)
			args.logfile.flush()
	sys.exit(0)

### Main terminal loop ###

try:

	while 1:
		incoming = ''.join(port.readlines())
		if incoming:
			if not args.quiet:
				print fmt(incoming),
			if args.logfile:
				print >> args.logfile, '<', fmt(incoming).strip().replace('\n', '\n< ')
				args.logfile.flush()

		try:
			cmd = prompt()
			if cmd:
				print >> port, cmd + args.eol,
				if args.logfile:
					print >> args.logfile, '>', cmd
		except EOFError:
			break

except KeyboardInterrupt:
	pass

finally:
	print "Bye."
	sys.exit(0)
