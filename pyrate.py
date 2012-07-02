# 
# Copyright (c) 2012, Remo Giermann <mo@liberejo.de>
# 
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH 
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# 

import serial
import time
from sys import stderr

def flat(*args):
	''' Make a flat list out of many arguments including nested
	lists or strings. '''
	r = []
	for a in args:
		if type(a) == str:
			r.extend(list(a))
		elif type(a) in (tuple, list):
			r.extend(flat(*a))
		else:
			r.append(a)
	return r

def bitreverse(byte, bits=8):
	''' Change bit order '''
	byte = ''.join(bit for bit in reversed("{:0"+str(bits)+"b}".format(byte)))
	return int(byte, 2)

class BB:
	''' BitBang commands '''
	reset_mode  = 0
	info        = 1
	enter_spi   = 1
	enter_i2c   = 2
	enter_uart  = 3
	enter_1wire = 4
	enter_raww  = 5
	enter_jtag  = 6

	reset_pirate = 15
	voltage      = 20
	voltage_cont = 21
	frequency    = 22

	pinconfig = 64
	setperiph = 128

	bulk_write = 16

class OWI:
	''' 1-Wire-only commands '''
	reset = 2
	read  = 4
	romsearch   = 8
	alarmsearch = 9

class SPI:
	''' SPI-only commands '''
	cslow  = 2
	cshigh = 3
	speed30k   = 96
	speed125k  = 97
	speed250k  = 98
	speed1M    = 99
	speed2M    = 100
	speed2M6   = 101
	speed4M    = 102
	speed8M    = 103
	config     = 128

class I2C:
	''' I2C-only commands '''
	pass

class RawPins:
	''' Pinmasks to use in BBIO1 mode '''
	power = 1<<6  # turn on power supply
	pullup = 1<<5 # enable pullups
	aux = 1<<4   
	mosi = 1<<3 
	clk = 1<<2
	miso = 1<<1
	cs = 1<<0

class PPins:
	''' Pinmasks to use in any other mode than BBIO1 '''
	power  = 1<<3  # turn on power supply
	pullup = 1<<2  # enable pullups
	aux = 1<<1     # activate AUX (3.3V)
	cs  = 1<<0     # activate CS

class SPIConfig:
	''' Bitmasks to configure SPI '''
	output3v3 = 1<<3 # active outputs instead of open-drain
	ckp = 1<<2      # clk polarity: idle high
	cke = 1<<1      # clk edge: active to idle
	smp = 1<<0      # sample time: end

class Pirate(object):

	def __init__(self, port="/dev/ttyUSB0", baudrate=115200, timeout=0.2, **kwargs):
		self.port = serial.Serial(port, baudrate, timeout=timeout, **kwargs)
		mode = self.sresponse(0)
		if self.sresponse(0) != "BBIO1":
			print >>stderr, "pirate is in terminal mode"
			self.response(10*'\n')
			self.response('#\n')
			self.wait()
			if not "BBIO1" in self.sresponse('\x00'*20):
				print >>stderr, "failed to enter BitBang mode."
			else:
				print >>stderr, "entered BitBang mode."
	
	def wait(self, t=.1):
		time.sleep(t)

	def sresponse(self, *data):
		''' Send data and return string response.
		Data might be any number of integers, strings or 
		(nested) lists of those. '''
		for datum in flat(data):
			if type(datum) != str:
				datum = chr(datum)
			self.port.write(datum)
			self.wait()
		return self.port.read(256)

	def response(self, *data):
		''' Send data and return response as a list of bytes (int).
		Data might be any number of integers, strings or 
		(nested) lists of those. '''
		return list(bytearray(self.sresponse(*data)))

	def command(self, byte):
		''' Sends the command byte and returns
		True or False based on the response (non-zero or zero). '''
		r = self.response(byte)
		if len(r) == 0 or r[0] == 0:
			return False
		else:
			return True

	def voltageprobe(self):
		hi, lo = self.response(BB.voltage)[:2]
		return ((hi<<8|lo)*2*3.3)/2**10

	def freqprobe(self):
		self.port.write(chr(BB.frequency))
		self.wait(1)
		a, b, c, d = bytearray(self.port.read(4))
		return d|c<<8|b<<16|a<<24
		
	def setpins(self, pins):
		''' Set or clear pins in BBIO1 mode,
		use bitmasks from RawPins for 'pins'. '''
		return self.command(BB.setperiph|(pins&0x7F))

	def setio(self, pins):
		''' Set pins as input or output in BBIO1 mode,
		use bitmasks from RawPins for 'pins'. '''
		return self.command(BB.pinconfig|(pins&0x1F))

	def setperiph(self, pins):
		''' In any other mode than BBIO1: 
		Set peripherals (power, pullups) and pins (aux, cs), 
		use bitmasks from PPins for 'pins'. '''
		return self.command(BB.pinconfig|(pins&0x0F))

	def transmit(self, *data):
		''' Transmit data to a slave device. Data can be any 
		number of integers, strings or (nested) lists of those. '''
		if not self.command(BB.bulk_write|(len(data)-1)):
			return []
		else:
			return self.response(*data[:16])

	def info(self):
		''' Return current mode string. Beware: In HiZ mode (BBIO1)
		this will enter SPI mode. '''
		return self.sresponse(BB.info)

