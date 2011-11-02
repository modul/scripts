#!/usr/bin/env python
#
# twall.py
# A very simple console app which displays a "twitter wall" with 
# only few features.
# It was supposed to be used on the Ben NanoNote.
# 
#  author: Remo Giermann
# created: 2010/05/17
# updates:
# 2010-05 added commands, retweeting, etc.
# 2010-06-07: commands supposed to work as expected 

__version__ = "0.1"
__author__  = "Remo Giermann"

import twitter
import signal
import readline
import sys
from string import join
from os import system
from time import sleep, localtime, strftime

__width=40
un='modul'
pw='zvfgrezo30'
interval=300
tweets_at_a_time=3
editor="/usr/bin/joe" 

tw_length=140 # u don't have to change this

# utility functions, printing especially

def get_input(prompt):
    argv = []
    try:
        inp = raw_input(prompt)
        inp = inp.strip().lower()
        argv = inp.split()
    except (KeyboardInterrupt, EOFError):
        pass
    
    return argv


def block(text, width=__width):
    """
    Fits a string `text` into the specified width by adding
    linebreaks.
    """
    counter = 0
    output = ''
    words = text.split()
    for word in words:
        l = len(word)
        if counter + l > width:
            output += '\n'+word+' '
            counter = l + 1
        elif counter + l == width:
            output += word+'\n'
            counter = 0
        else:
            output += word + ' '
            counter += l + 1

    return output

def shorten(t, length):
    if len(t) <= length:
        return t
    else:
        return t[:length-3]+'...'

def print_tweet(s, id=None, relative_time=True):
    """
    Prettily prints the tweet `s`.
    """
    n = s.user.screen_name.encode('utf8')
    if id is not None:
        n = '(%i) %s' % (id, n)
    if relative_time == True:
        t = s.relative_created_at
    else:
        t = strftime('%H:%M (%a, %b %d)', localtime(s.created_at_in_seconds))
    pad = __width - len(n) - len(t)
    if pad <= 0:
      pad = __width - len(n)

    print "%s%s%s" % (n,pad * ' ',t)
    text = s.text.encode('utf8')
    print block(text)
    print "~".center(__width)

def print_n(tweets, count, *args, **kwargs):
    for i in range(count):
        print_tweet(latest[count - i - 1], *args, **kwargs)

def print_dense_list():
    """
    Prints a dense list of shortened and numbered tweets.
    Oldest to newest tweets.
    """
    system('clear')
    count = len(latest)
    tweets = latest[:]
    tweets.reverse()
    for i in range(len(tweets)):
        s = tweets[i]
        num = count - i - 1
        name = s.user.screen_name.encode('utf8')
        l = __width - 15 - len(name)
        text = shorten(s.text.encode('utf8'), l)
        time = s.created_at_in_seconds
        time = strftime('%H:%M:%S', localtime(time))
        print "(%2i) %s %s %s" % (num, name, text, time)

def print_help():
    htext="twall.py - a very simple console application to display recent tweets."
    print block(htext)
    print 'v%s by %s' % (__version__, __author__ )
    print "\nCommands: "
    print "h[elp], q[uit]"
    print "rt - select a tweet to RT it"
    print "t[weet] - post a new tweet"
    print "l[atest] - prints all latest tweets"
    print "r[eply] - reply to a tweet"
    print "<RETURN> - refreshes timeline"
    print
    print "CTRL-C cancels any operation."

def display(count=tweets_at_a_time):
    """ Main tweet display. """
    system('clear')
    print_n(latest, count)

# commands one my fire up

def cmd_retweet(i):
    system('clear')
    s = latest[i]
    
    leader = "RT @%s: " % s.user.screen_name
    old = s.text
    s.text = leader + s.text
    s.text = shorten(s.text, tw_length)
    print_tweet(s)
    
    ans = get_input("[c]ancel, [return] to tweet: ")
    
    if len(ans) > 0 and ans[0] == 'c':
        s.text = old
        return
    else:
        api.PostUpdate(s.text)
        s.text = old

def cmd_tweet():
    system('clear')
    text = ""
    try:
        text = raw_input("Type your tweet:\n")
        if len(text) == 0 or text.isspace():
            return
    except:
        return
    else:
        while len(text) > tw_length:
            print "Update mustn't be longer than"
            print "\n %i characters - yours was %i" % (tw_length, len(text))
            try:
                text = raw_input("Try it again:\n")
                if len(text) == 0 or text.isspace():
                    return
            except:
                return
                
        api.PostUpdate(text)

def cmd_reply(i):
    system('clear')
    s = latest[i]
    to = s.user.screen_name
    text = "@%s" % to
    
    print "Type your reply:"
    try:
        ans = raw_input(text)
        if len(ans) == 0 or ans.isspace():
            return
    except:
        return
    else:
        while len(text + ans) > tw_length:
            print "Update mustn't be longer than"
            print "\n %i characters - yours was %i" % (tw_length, len(text+ans))
            print "Try it again: "
            try:
                ans = raw_input(text)
                if len(ans) == 0 or ans.isspace():
                    return
            except:
                return
        
        text += ans
        api.PostUpdate(text)

# things to control the mainloop

class Refresh(Exception):
    pass

def handler(signum, frame):
    raise Refresh

signal.signal(signal.SIGALRM, handler)

# initialization
api = twitter.Api(username=un, password=pw)
try:
  latest = api.GetFriendsTimeline(un)
except:
  print "Unable to initially fetch tweets. Network down?"
  sys.exit(1)
else:
  last_checked = localtime()
  
# initially print all tweets, from old to new
system('clear')
tweets = latest[:]
tweets.reverse()
for i in tweets:
    print_tweet(i, relative_time=False)

# main loop in which to check and print new tweets

while 1:
    try:
        signal.alarm(interval)
        prompt = "(%s) " % strftime('%H:%M:%S', last_checked)
        argv = get_input(prompt) 
        signal.alarm(0)

        argc = len(argv)
        if argc == 0:
            raise Refresh

        if argv[0] in ('q', 'quit'):
            break

        elif argv[0] in ('l', 'latest'):
            display(len(latest))

        elif argv[0] == 'rt':
            print_dense_list()
            print
            ans = get_input("Tweet number or return key: ")
            if len(ans) > 0 and ans[0].isdigit():
                cmd_retweet(int(ans[0]))
            display()
        
        elif argv[0] in ('r', 'reply'):
            print_dense_list()
            print
            ans = get_input("Tweet number or return key: ")
            if len(ans) > 0 and ans[0].isdigit():
                cmd_reply(int(ans[0]))
            display()

        elif argv[0] in ('h', 'help'):
            system('clear')
            print_help()
            raw_input("\nPress return key to go back... ")
            display()
        
        elif argv[0] in ('t', 'tweet'):
            cmd_tweet()
            display()

    except Refresh:
        try: 
            tweets = api.GetFriendsTimeline(un)
            last_checked = localtime()
        except:
            pass
        if tweets != latest:
            latest = tweets
        display()
