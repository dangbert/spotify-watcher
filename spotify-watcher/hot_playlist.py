#!/usr/bin/env python3
# source secret.env before running this program!

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import json

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
#from pytz import UTC as utc
import pytz

# global constants
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
username = 'dangbert' # TODO: look for way to get this from playlist uri... (or set in ENV)

def main():
    #uri = 'spotify:user:dangbert:playlist:40dcGwdCvUDFwS893qdaLd' # old uri style
    uri = 'spotify:playlist:40dcGwdCvUDFwS893qdaLd'  # modern uri

    hot_playlist(60, uri)

# remove all songs older than daysOldLimit from given playlist
def hot_playlist(daysOldLimit, list_uri):
    # TODO: ensure this works with very long playlists (over 100 songs)
    results = sp.user_playlist(username, list_uri.split(':')[2])
    #print(json.dumps(results, indent=4))

    now = timeNowUTC()
    print("now = " + str(now))
    for item in results["tracks"]["items"]:
        # calculate the time elapsed since track was added to playlist
        dateStr = item["added_at"] # e.g. "2019-11-12T04:21:15Z"
        if dateStr == None:
            print("dateStr is None")
        addDate = parser.parse(dateStr) # magic date parser

        # get the delta time since playlist was added
        delta = relativedelta(now, addDate)
        print("delta = " + str(delta.days) + " days, " + str(delta.hours) + " hours")
        #print(str(addDate) + '\t"' + item["track"]["name"] + '"')

# returns datetime for the UTC time now (location aware)
# (can be used for relativedelta calculations)
def timeNowUTC():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

if __name__ == "__main__":
    main()
