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

### Convert bytes of strings to hex, binary or decimal dumps ###

def digits(converter):
	''' Returns the number of digits produced by converter '''
	if converter is None:
		return 0
	else:
		return len(converter("\xff").next())

def hexs(text):
	''' Yields hex representation for bytes in text '''
	for x in bytearray(text):
		yield "{:02x}".format(x)

def bins(text):
	''' Yields binary representation for bytes in text '''
	for x in bytearray(text):
		yield "{:08b}".format(x)

def decs(text):
	''' Yields decimal representation for bytes in text '''
	for x in bytearray(text):
		yield "{: 3d}".format(x)

def convert(text, converter):
	''' Converts text to hex, bin or decimal dump '''
	return ' '.join(converter(text))

def paragraph(text, bytelen, bytenum):
	''' Formats a string dump text with paragraphs.
	bytelen is the number of characters needed for one byte (digits),
	bytenum is the number of bytes to be on one line.
	'''
	return fill(text, (bytelen+1)*bytenum)+'\n'


### Process command line arguments ###

def factory(options, port):
	''' Build helper functions based on 'options'. '''
	from time import strftime

	if options.converter is None:
		def fmt(text):
			return text
	else:
		def fmt(text):
			return paragraph( \
					convert(text, options.converter),\
					digits(options.converter)+1,\
					options.width)

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

	if options.quiet is True:
		def printer(text):
			pass
	else:
		def printer(text):
			print text,
	
	if options.logfile:
		def logger(text):
			print >>options.logfile, text,
			args.logfile.flush()
	else:
		def logger(text):
			pass

	return prompt, fmt, printer, logger

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
group.add_argument("--hex", dest="converter", action="store_const", const=hexs, default=None)
group.add_argument("--binary", dest="converter", action="store_const", const=bins, default=None)
group.add_argument("--decimal", dest="converter", action="store_const", const=decs, default=None)
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

prompter, formatter, printer, logger = factory(args, port)

if args.commands:
	for cmd in args.commands:
		port.write(cmd+eol)

	incoming = ''.join(port.readlines())
	if incoming:
		incoming = formatter(incoming)
		printer(incoming)
		logger(incoming)
	sys.exit(0)

#----------------------------------------------------------

try:

	while 1:
		incoming = ''.join(port.readlines())
		if incoming:
			incoming = formatter(incoming)
			printer(incoming)
			logger("< "+incoming)

		try:
			cmd = prompter()
			if cmd:
				port.write(cmd+eol)
				logger("> "+cmd+'\n')
		except EOFError:
			break

except KeyboardInterrupt:
	pass

finally:
	print "Bye."
	sys.exit(0)
