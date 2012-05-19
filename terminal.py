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

### Process command line arguments and build helper functions ###

def formatter(converter=None, width=0):
	''' Build a string formatting function.
	If converter is one of hexs, bins or decs, width is the number of bytes
	to put on one line. If converter is None, given text is returned
	untouched. '''
	if converter:
		chars = width * (digits(converter) + 1)
		def fmt(text):
			txt = ' '.join(converter(text))
			return fill(txt, chars)+'\n'
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

def printer(quiet=False):
	''' Build a function that prints text if quiet is True, otherwise 
	the function does nothing.
	'''
	if quiet:
		def printit(text):
			pass
	else:
		def printit(text):
			print text.strip()
	return printit

def logger(fp=None):
	''' Build a function that logs text to fp if present, or does nothing. '''
	if fp:
		def logit(text):
			print >> fp, text.strip()
			fp.flush()
	else:
		def logit(text):
			pass
	return logit

def sender(port=None, eol='\n'):
	''' Build a function that sends arbitrary text (including 
	newline characters) through port.
	'''
	if port:
		def send(text):
			port.write(text+eol)
	else:
		def send(text):
			pass
	return send

def receiver(port=None, fmt=None):
	''' Build a function that reads all input from port and returns it,
	formatted using fmt, if given. 
	'''
	if port:
		if fmt:
			def receive():
				return fmt(''.join(port.readlines()))
		else:
			def receive():
				return ''.join(port.readlines())
	else:
		def receive():
			pass
	return receive


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
parser.add_argument("--logfile", metavar="FILE", type=FileType(mode="w"), help="log everything to FILE")
parser.add_argument("--eol", default="lf", choices=["lf", "crlf", "cr", "lfcr", "none"], help="choose end of line characters (lf)")

group = parser.add_argument_group("Format")
group.add_argument("--hex", dest="converter", action="store_const", const=hexs, default=None)
group.add_argument("--binary", dest="converter", action="store_const", const=bins, default=None)
group.add_argument("--decimal", dest="converter", action="store_const", const=decs, default=None)
group.add_argument("--width", default=8, type=int, help="how much bytes to display in a line")

group = parser.add_argument_group("Prompt")
group.add_argument("--prompt", metavar="STR", default="> ", help="show STR as prompt; might include strftime-like formatting")
group.add_argument("--prompt-cmd", metavar="CMD", help="show response to CMD in every prompt")

args = parser.parse_args()
args.eol = args.eol.replace("lf", "\n").replace("cr", "\r").replace("none", "")

try:
	port = serial.Serial(args.device, args.baudrate, timeout=args.timeout)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)

#----------------------------------------------------------

cmd = args.prompt_cmd and args.prompt_cmd+args.eol or None

logit    = logger(args.logfile)
printit  = printer(args.quiet)
prompt   = prompter(args.prompt, cmd, port)
formatit = formatter(args.converter, args.width)
send     = sender(port, args.eol)
receive  = receiver(port, formatit)

if args.commands:
	for cmd in args.commands:
		send(cmd)

	incoming = receive()
	if incoming:
		printit(incoming)
		logit(incoming)
	sys.exit(0)

#----------------------------------------------------------

try:

	while 1:
		incoming = receive()
		if incoming:
			printit(incoming)
			logit("< "+incoming)

		try:
			cmd = prompt()
			if cmd:
				send(cmd)
				logit("> "+cmd+'\n')
		except EOFError:
			break

except KeyboardInterrupt:
	pass

finally:
	print "Bye."
	sys.exit(0)
