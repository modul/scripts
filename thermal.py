#!/usr/bin/env python 
# 
# All rights reversed.
# 2012 Remo Giermann <mo@liberejo.de>
# 

import SocketServer
import socket
from time import strftime
from sys import argv, stderr, stdin, exit

LPT = "/dev/usb/lp0"
WIDTH = 24
EOL = '\r'

def lineprinter(portstr):
	""" Try opening printer port,
	on success, returns a printing function, otherwise None. """
	try: port = open(portstr, "wb")
	except IOError:
		print >>stderr, "could not open printer port", args.port
		exit(1)
	def lp(line=None):
		if line is not None:
			line = line.strip().decode('utf8').encode('cp437', 'ignore')
			port.write(line)
			if len(line) != WIDTH: # feeds automatically after WIDTH characters
				port.write(EOL)
	return lp

def timestamp():
	return strftime("%y/%m/%d %H:%M")

def shorten(string, width=80, append='...'):
	if len(string) > 80: return string[:width-len(append)]+append

class PrintHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data, socket = self.request
		ip = self.client_address[0]
		print >>stderr, timestamp(), ip, ' '.join(data.split('\n'))
		try: 
			lp = lineprinter(self.server.printerport)
			sender = ip.replace(':', '').replace('.', '')
			lp("{} {}".format(timestamp(), sender[-8:]))
			lp(data)
			lp("-"*(WIDTH-1))
			r = "SUCCESS"
		except SystemExit:
			r = "NO PORT"
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
	parser.add_argument("-t", action="store_true", dest="time", help="add timestamp", default=False)
	parser.add_argument("-l", action="store_true", dest="line", help="append horizontal line", default=False)
	parser.add_argument("-s", action="store_true", dest="serve", help="serve via UDP6:2323", default=False)
	args = parser.parse_args(argv[1:])
	
	try:
		if args.serve:
			server = PrintServer(args.port, ("", 2323), PrintHandler)
			server.serve_forever()
		else:
			lp = lineprinter(args.port)
			if args.time: lp(timestamp())
			for line in args.file: lp(line)
			lp(args.line and '-'*(WIDTH-1) or None)
	except KeyboardInterrupt:
		print >>stderr, "terminated ..."
