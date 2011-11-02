#!/usr/bin/env python
# 
# This script fetches the messages/tweets/history from your Twitter feed.
# It is meant to be included in another script or run in a python shell.
#
# Remo Giermann <rgiermann@liberejo.de>
# 2010/10/26
#

import sys, time, json, urllib, re

__feedurl           = "http://api.twitter.com/1/statuses/user_timeline.json"
__max_pagecount     = 16
__debug             = True

def debug(s):
    if __debug:
        print s,

def convert_datetime(tstring):
    """Convert twitter's 'created_at' date/time-format to ISO-format."""
    try:
        t = tstring.replace('+0000', '')
        return time.strftime("%Y-%m-%d %H:%M UTC", time.strptime(t))
    except:
        return tstring

def strip_html(data):
    """Get rid of HTML"""
    p = re.compile(r'<.*?>')
    return p.sub('', data)
    
    
    
def fetch_tweets(username, pages=1, count=20, include_rt=True):
    """
    Fetches JSON feed of twitter history. 
    Returns a list containing one dictionary per tweet (resembling the JSON 
    structure). With default arguments, the 20 most recent messages will be
    fetched.
    
    Arguments:
    ----------
    username: the screen name of the user's feed
    pages:    number of pages to be fetched (default: 1, max: 16)
    count:    number of messages per page (default: 20, max: 200)
    include_rt: wether or not including ReTweets in fetched messages 
                (default: True)
    """
    
    if pages > 1:
        s = 's'
    else:
        s = ''
        
    debug("Attempting to fetch %i page%s of %s's twitter feed.\n" % (pages, s, username))

    if pages > __max_pagecount:
        pages = __max_pagecount
        debug("Count exceeds maximum (%i).\n" % __max_pagecount)
    elif pages <= 0:
        pages = 1
        
    if count == 0:
        count = 20
        
    tweets = []
    for p in range(1,pages+1):
        url = __feedurl + "?screen_name=%s&include_rts=%i&page=%i&count=%i" % (username, include_rt, p, count)
        debug("Fetching page %i..." % p)
        feed = urllib.urlopen(url).readline()
        debug("done.\n")
        tweets += json.loads(feed)
        
    return tweets

def fetch_all_tweets(username, include_rt=1):
    """
    Try to get all messages from the feed (twitter limits this to 3200).
    
    Arguments:
    ----------
    username: the screen name of the user's feed
    include_rt: wether or not including ReTweets in fetched messages 
                (default: True)
                
    Returns a list of dictionaries.
    """
    
    return fetch_tweets(username, pages=16, count=200, include_rt=include_rt)
    
def print_tweets(tweets):
    """
    Prints `tweets` (returned from fetch_tweets() or simplify_tweets()).
    
    Arguments:
    ----------
    tweets:  list of dictionaries (returned from fetch_tweets, fetch_all_tweets
              or simplify_tweets)
    """
    
    for t in tweets:
        print t['text']
        print strip_html(t['source'])
        print convert_datetime(t['created_at'])
        print

def simplify_tweets(tweets):
    """ 
    Generates a simplified JSON structure from `tweets`.
    
    Arguments:
    ----------
    tweets:  list of dictionaries (returned from fetch_tweets or fetch_all_tweets.
    
    Returns a list of dictionaries resembling a simplified JSON-structure 
    containing only id, text, time and source of messages.
    """

    jtweets = []
    for t in tweets:
        d =  {'id':t['id'], 'text':t['text'], 'source':strip_html(t['source']), 'created_at': convert_datetime(t['created_at'])}
        jtweets.append(d)
    
    return jtweets

def tweets_to_file(tweets, fp, indent=4, as_json=True):
    """
    Takes `tweets` and writes either a simplified JSON-structure or text to the
    file pointed to by `fp`.
    
    Arguments:
    ----------
    tweets:  list of dictionaries (returned from fetch_tweets, fetch_all_tweets
              or simplify_tweets)
    fp:      a writable file pointer
    indent:  indentation level of JSON file (default: 4, 0 to only include newlines)
    as_json: wether to write JSON or text to `fp` (default: True)
    """
    
    if as_json is True:
        if len(tweets[0]) > 3:
            tweets = simplify_tweets(tweets)
            
        for t in tweets:
            json.dump(t, fp, indent=indent)
            
    else:
        for t in tweets:
            fp.write(t['text'].encode('utf8')+'\n')
            fp.write(strip_html(t['source']).encode('utf8')+'\n')
            fp.write(convert_datetime(t['created_at']).encode('utf8')+'\n\n')
    
    fp.flush()