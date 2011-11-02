#!/usr/bin/python

# 
# amarok.py
# 
# This script controls a running amarok using its DBus interface.
# Useful on the commandline or within other applications/scripts.
#
#----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mo@liberejo.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
#
# 2010/02/11
#

import commands
from sys import argv, exit
import urllib

# default values
_volume_step = 5

# DBus resources
_dbus_service   = "org.kde.amarok"
_dbus_object   = "/Player"
_dbus_objpath   = "org.freedesktop.MediaPlayer"
_dbus_qry_cmd = "qdbus"

# The wrapper class to interface with amarok
class Player:
    def __init__(self):
       self.__checkRunning()
    
    def __makeCmdString(self, cmd):
        return "%s %s %s %s.%s" % (_dbus_qry_cmd, _dbus_service, _dbus_object, _dbus_objpath, cmd)

    def __doCommand(self, cmd):
        cmd_string = self.__makeCmdString(cmd)
        (status, output) = commands.getstatusoutput(cmd_string)
        
        if status == 0:
            self.running = True
            return output
        else:
            self.running = False
            return ''
    
    def __checkRunning(self):
        st = _dbus_qry_cmd + ' ' + _dbus_service
        (status, output) = commands.getstatusoutput(st)

        if status == 0:
            self.running = True
        else:
            self.running = False

        return self.running

    def __quitAmarok(self):
       if not self.running:
           return

       cmd_string = _dbus_qry_cmd + ' ' + _dbus_service + ' /MainApplication org.kde.KApplication.quit'
       commands.getoutput(cmd_string)
       self.running = False
        
    def __findMetaKey(self, searchstring):

        meta    = self.get_metadata()

        if not self.running:
            return ''

        lines   = meta.split('\n')
        search  = searchstring + ': '
        l       = len(search)
        
        for line in lines:
            if line[:l] == search:
                return line[l:]

    def isRunning(self):
        return self.running

    def isStopped(self):
        if not self.get_track_fileurl():
            return True
        else:
            return False

    def quit(self):
        self.__quitAmarok()

    def next(self):
        self.__doCommand('Next')

    def prev(self):
        self.__doCommand('Prev')

    def playpause(self):
        self.__doCommand('PlayPause')

    def stop(self):
        self.__doCommand('Stop')

    def osd(self):
        self.__doCommand('ShowOSD')

    def mute(self):
        self.__doCommand('Mute')
    
    def volup(self):
        self.__doCommand('VolumeUp '+str(_volume_step))

    def voldown(self):
        self.__doCommand('VolumeDown '+str(_volume_step))

    def set_volume(self, volume_percent):
        self.__doCommand('VolumeSet '+str(volume_percent))

    def get_volume(self):
        return self.__doCommand('VolumeGet')
    
    def get_metadata(self):
        return self.__doCommand('GetMetadata')

    def get_track_artist(self):
        return self.__findMetaKey('artist')

    def get_track_album(self):
        return self.__findMetaKey('album')

    def get_track_title(self):
        return self.__findMetaKey('title')

    def get_track_number(self):
        return self.__findMetaKey('tracknumber')
    
    def get_track_year(self):
        return self.__findMetaKey('year')

    def get_track_genre(self):
        return self.__findMetaKey('genre')

    def get_track_bitrate(self):
        return self.__findMetaKey('audio-bitrate')

    def get_track_coverurl(self):
        return self.__findMetaKey('arturl')

    def get_track_fileurl(self):
        return self.__findMetaKey('location')

#### Main Code ####

p = Player()

if len(argv) < 2:
    print """
commands: 
 stopped            check if amarok has stopped playback
 running, r         check if amarok is running
 quit               quit amarok
 playpause, c       toggle play/pause
 stop, v
 prev, b           
 next, n           
 mute, m           
 volup, u           volume up by 5
 voldn, d           volume down by 5
 osd, o             shows OSD
 info, i            returns title information
 title, tt          returns title only
 artist, at         returns artist only
 titleartist, ta    returns "TITLE by ARTIST"
 album, ab          returns album
 albumyear, ay      returns "ALBUM (YEAR)" if year is not empty
 genre, gr          returns genre
 year, yr
 bitrate, br
 number, tn         returns track number
 file, fp           returns path to playing track
 cover, cv          returns path to cover art
"""

else:
    c = argv[1]

    if not p.isRunning():
        if c in ('r','c','v','b','n','m','u','d','o', 'stopped', 'running', 'playpause','stop','prev','next','voldn','volup','osd'):
            print "Amarok 2 is not running."
        exit(1)
    else:
        if c in ('r', 'running'):
            print "Yes!"
            exit(0)

    if c == 'quit':
        p.quit()
        exit()

    elif c == 'stopped':
        print p.isStopped()

    elif c in ('stop', 'v'):
        p.stop()
    elif c in ('playpause', 'c'):
        p.playpause()
    elif c in ('prev', 'b'):
        p.prev()
    elif c in ('next', 'n'):
        p.next()
    elif c in ('mute', 'm'):
        p.mute()
    elif c in ('volup', 'u'):
        p.volup()
    elif c in ('voldn', 'd'):
        p.voldown()
    elif c in ('osd', 'o'):
        p.osd()
    elif c in ('info', 'i'):
        if p.isStopped():
            print "Amarok has stopped playback."
            exit(0)

        t = p.get_track_title()
        a = p.get_track_artist()
        b = p.get_track_album()
        y = p.get_track_year()
        n = p.get_track_number()
        g = p.get_track_genre()

        year = ''
        track = ''
        genre = ''
        album = ''

        if y and len(y) == 4:
            year = " (%s)" % y
        if int(n) > 0:
            track = 'Track %s ' % n
        if g not in ('', ' '):
            genre = "It's %s!" % g
        if b not in ('', ' ', 'Unknown'):
            album = 'on ' + b

        print "Playing %s by %s\n%s%s%s\n%s" % (t, a, track, album, year, genre)
        
    elif c in ('title', 'tt'):
        t = p.get_track_title()
        if t: 
            print t

    elif c in ('artist', 'at'):
        t = p.get_track_artist()
        if t:
            print t

    elif c in ('titleartist', 'ta'):
        a = p.get_track_artist()
        t = p.get_track_title()

        if a == None and t == None:
            print "Not playing anything."
            exit(0)
        
        print "%s by %s" % (t, a)

    elif c in ('album', 'ab'):
        t = p.get_track_album()
        if t:
            print t

    elif c in ('albumyear', 'ay'):
        a = p.get_track_album()
        y = p.get_track_year()

        if y and len(y) == 4:
            year = '(%s)' % (y)
        else:
            year = ''

        if a in ('Unknown', '', ' ', None):
            album = year
        else:
            album = a + ' ' + year
            
        if album:
            print album

    elif c in ('genre', 'gr'):
        t = p.get_track_genre()
        if t: 
            print t 

    elif c in ('year', 'yr'):
        t = p.get_track_year()
        if t and len(t) == 4:
            print t

    elif c in ('bitrate', 'br'):
        print p.get_track_bitrate()

    elif c in ('cover', 'cv'):
        f = p.get_track_coverurl()

        if f:
            if f[:7] == 'file://':
                f = f[7:]

            print urllib.unquote(f)

    elif c in ('file', 'fp'):
        f = p.get_track_fileurl()
        
        if f:
            if f[:7] == 'file://':
                f = f[7:]

            print urllib.unquote(f)

    else:
        print 'Unknown command!'
        exit(1)
