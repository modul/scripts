#!/usr/bin/env python
# apmosd.py
#
# This script shows APM information on screen 
#
# written by mo 2007/07/13
#


from os import popen
from pyosd import *

### CONFIGURATION

__timeout = 3
__colour  = "#FF2222"
__font =  "-*-helvetica-bold-r-normal-*-*-200-*-*-p-*-*-*"
__shadow_offset = 1
__position = POS_TOP # POS_BOT or POS_TOP
__offset = 0 # vertical offset from __position
__align = ALIGN_RIGHT # ALIGN_CENTER, ALIGN_LEFT or ALIGN_RIGHT
__hoffset = 0 # horizontal offset from __align

### PREPARING OSD 

o = osd()
o.set_timeout(__timeout)
o.set_colour(__colour)
o.set_font(__font)
o.set_shadow_offset(__shadow_offset)
o.set_pos(__position)
o.set_offset(__offset)
o.set_align(__align)
o.set_horizontal_offset(__hoffset)

### GETTING INFO

fp = popen("apm")
string = fp.readlines()[0]
fp.close()

### DISPLAYING

o.display(string)

while o.is_onscreen():
	pass

