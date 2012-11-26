#!/usr/bin/env python 
# 
# All rights reversed.
# 2012 Remo Giermann <mo@liberejo.de>
# 

import SocketServer
import socket
from time import strftime
from sys import argv, stderr, stdin, exit
from textwrap import wrap

LPT = "/dev/usb/lp0"
WIDTH = 24
LINE = '-'*WIDTH
EOL = '\r'

def timestamp():
	return strftime("%y/%m/%d %H:%M")

def lineprinter(portstr, wrapping="none"):
	""" Try opening printer port and return a printing function

	'wrapping' might be 'none', 'truncate' or 'wrap'
	"""
	try: port = open(portstr, "wb")
	except IOError:
		print >>stderr, "could not open printer port", args.port
		return None
	
	if wrapping == 'truncate':
		wrapped = lambda l: [l[:WIDTH]]
	elif wrapping == 'wrap':
		wrapped = lambda l: wrap(l, WIDTH) or ['']
	else:
		wrapped = lambda l: [l]

	def lp(line=None):
		if line is not None:
			line = line.strip().decode('utf8').encode('cp437', 'ignore')
			for part in wrapped(line):
				port.write(part)
				if len(part) != WIDTH: # feeds automatically after WIDTH characters
					port.write(EOL)
	return lp

class PrintHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data, socket = self.request
		ip = self.client_address[0]
		sender = ip.replace(':', '').replace('.', '')
		print >>stderr, timestamp(), ip, ' '.join(data.split('\n'))

		lp = lineprinter(self.server.printerport)
		if lp: 
			lp("{} {}".format(timestamp(), sender[-8:]))
			lp(data)
			lp(LINE)
			r = "SUCCESS"
		else: r = "NO PORT"
		socket.sendto(r+'\n', self.client_address)

class PrintServer(SocketServer.UDPServer):
	address_family = socket.AF_INET6
	def __init__(self, lpt, *args, **kwargs):
		SocketServer.UDPServer.__init__(self, *args, **kwargs)
		self.printerport = lpt

if __name__ == "__main__":
	from argparse import ArgumentParser, FileType
	parser = ArgumentParser(description="Thermal Printer Frontend")
	parser.add_argument("file", nargs='?', help="file to print (stdin)", type=FileType('r'), default=stdin)
	parser.add_argument("-p", metavar="PORT", dest="port", help="printer port "+LPT, default=LPT)
	parser.add_argument("-t", action="store_const", dest="wrap", const="truncate", help="truncate lines", default=False)
	parser.add_argument("-w", action="store_const", dest="wrap", const="wrap", help="wrap lines", default=False)
	parser.add_argument("-d", action="store_true", dest="time", help="add date", default=False)
	parser.add_argument("-l", action="store_true", dest="line", help="append horizontal rule", default=False)
	parser.add_argument("-s", action="store_true", dest="serve", help="serve via UDP6:2323", default=False)
	args = parser.parse_args(argv[1:])
	
	try:
		if args.serve:
			server = PrintServer(args.port, ("", 2323), PrintHandler)
			server.serve_forever()
		else:
			lp = lineprinter(args.port, args.wrap) or exit(1)
			if args.time: lp(timestamp())
			for line in args.file: lp(line)
			lp(args.line and LINE or None)
	except KeyboardInterrupt:
		print >>stderr, "terminated ..."
