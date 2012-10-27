#!/usr/bin/env python 
import SocketServer
import socket
from time import strftime
from sys import argv, stderr, exit

LPT = "/dev/usb/lp0"
WIDTH = 24
EOL = '\r'

def lineprinter(portstr):
	""" Try opening printer port,
	on success, returns a printing function, otherwise None. """
	try: port = open(portstr, "wb")
	except IOError: return None

	def lp(data):
		print >>port, data.decode('utf8').encode('cp437', 'ignore'), EOL
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
		lp = lineprinter(self.server.printerport)
		if lp:
			sender = ip.replace(':', '').replace('.', '')
			lp("{} {}".format(timestamp(), sender[-8:]))
			lp(data)
			lp("-"*WIDTH)
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
	parser.add_argument("-p", metavar="PORT", dest="port", help="printer port (/dev/usb/lp0)", default=LPT)
	parser.add_argument("-t", action="store_true", dest="time", help="add timestamp", default=False)
	parser.add_argument("-l", action="store_true", dest="line", help="add horizontal line", default=False)
	parser.add_argument("-s", action="store_true", dest="serve", help="listen on UDP6:2323", default=False)
	args = parser.parse_args(argv[1:])
	
	if args.serve:
		server = PrintServer(args.port, ("", 2323), PrintHandler)
		server.serve_forever()
	else:
		lp = lineprinter(args.port)
		if not lp:
			print >>stderr, "could not open printer port", args.port
			exit(1)
		try:
			if args.time: lp(timestamp())
			while True:
				lp(raw_input())
		except (EOFError, KeyboardInterrupt):
			if args.line: lp('-'*WIDTH)
			else: lp("")
