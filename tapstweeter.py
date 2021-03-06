#!/usr/bin/python
import tweepy
import time
import sys
import requests
import json
import os
import csv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = CURRENT_DIR + '/sent_cache'
SITE_URL = 'http://taps-aff.co.uk'

# Load API keys
from config import API_KEYS

def generate_location_date_filename(location):
    return CACHE_DIR + '/' + location + '-' + time.strftime('%Y-%m-%d') + '.csv'

# Check if the weather is "aff" in given location
# Returns the status from taps-aff if True,
# otherwise returns None.
def get_taps_status(location):
    """Returns True if taps aff for this location"""

    request = requests.get('http://www.taps-aff.co.uk/api/%s' % location)
    if request.status_code == 200:
        try:
            taps = request.json()
            if taps['taps']['status'] == 'aff':
                return taps
            elif taps == 'oan':
                return None
            else:
                return None
        except ValueError:
            return None
    else:
        return None

# Write the taps-aff status to a csv file
def stash_tapsaff_info(status, filename):
    w = csv.writer(open(filename, 'w'))
    for (key, val) in status.items():
        w.writerow([key, val])

# [Redundant Abstraction #1]
def tweet_already_sent(filename):
    return os.path.isfile(filename)

# Attempt to send tweet and return True if
# successful or False if there was a problem
def send_tweet(tweet):
    # API_KEYS pulled in from config.py
    try:
        api = get_api(API_KEYS)
        print ('Attempting to tweet[%d]: %s' % (len(tweet), tweet))
        _ = api.update_status(status=tweet)
        return True

    except tweepy.error.TweepError:
        print ('Error sending tweet')
        return False

def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)

def main(location):
    # Location to dump info if it's Taps Aff
    cache_file = generate_location_date_filename(location)

    if tweet_already_sent(cache_file):
        print ('Already sent a tweet about %s ' % location)
        return

    # Check if it's Taps Aff. If it is
    # then send a tweet about it. If the
    # tweet is successfull then save the
    # info of the even in cache_file.
    taps_data = get_taps_status(location)
    if taps_data != None:
        message = 'Officially #TapsAff in %s! %s #iamarobot' % (location.upper(), SITE_URL)
        print(message)
        success = send_tweet(message)
        if success:
            stash_tapsaff_info(taps_data, cache_file)
    else:
        print ('Taps Oan in %s' % location)

if __name__ == '__main__':
    # Must specify a single-word location
    if len(sys.argv) > 1:
        location = sys.argv[1]
        main(location)
    else:
        print ('No location specified')
