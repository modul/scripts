#!/usr/bin/env python
#
# Very simple serial terminal
#
# If serial data is present, prints it.
# Afterwards, in any case, waits for user input.
#
# terminal.py DEVICE [BAUDRATE] [TIMEOUT]
#

import sys
import serial
import readline
from time import strftime
from textwrap import fill
from argparse import FileType, ArgumentParser, REMAINDER

__version__ = "1.0"

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

group = parser.add_argument_group("Prompt")
group.add_argument("--prompt", metavar="STR", default="> ", help="show STR as prompt; might include strftime-like formatting")
group.add_argument("--prompt-cmd", metavar="CMD", help="show response to CMD in every prompt")

args = parser.parse_args()
eol = args.eol.replace("lf", "\n").replace("cr", "\r")

try:
	port = serial.Serial(args.device, args.baudrate, timeout=args.timeout)
except serial.serialutil.SerialException as msg:
	print msg
	sys.exit(1)


def promptcmd(cmd=args.prompt_cmd, port=port, eol=eol):
	ret = ""
	if cmd and port:
		port.write(cmd+eol)
		ret = port.readline()
		if ret.endswith("\n"):
			ret = ret[:-1]
	return ret


if "%" in args.prompt:
	prmstr = lambda: strftime(args.prompt)
else:
	prmstr = lambda: args.prompt

if args.prompt_cmd:
	prompt = lambda: promptcmd(args.prompt_cmd, port, eol) + " " + prmstr()
else:
	prompt = prmstr


if args.commands:
	for cmd in args.commands:
		port.write(cmd+eol)

	incoming = ''.join(port.readlines())
	if incoming:
		if not args.quiet:
			print incoming,
		if args.logfile:
			print >>args.logfile, incoming,
	sys.exit(0)


try:
	while 1:
		incoming = ''.join(port.readlines())
		if incoming:
			if not args.quiet:
				print incoming,
			if args.logfile:
				print >> args.logfile, "< "+incoming,

		try:
			cmd = raw_input(prompt())
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
