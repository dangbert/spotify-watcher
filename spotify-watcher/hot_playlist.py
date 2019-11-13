#!/usr/bin/env python3
# source secret.env before running this program!

import spotipy
import spotipy.util as util
#from spotipy.oauth2 import SpotifyClientCredentials

import pprint
import json

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz


# global constants
username = 'dangbert' # TODO: look for way to get this from playlist uri... (or set in ENV)
scope = 'playlist-modify-public'
token = util.prompt_for_user_token(username, scope)
if not token:
    print("Can't get token for", username)
    exit(1)
sp = spotipy.Spotify(auth=token)
sp.trace = False

#client_credentials_manager = SpotifyClientCredentials()
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# TODO: use args
def main():
    #uri = 'spotify:user:dangbert:playlist:40dcGwdCvUDFwS893qdaLd' # old uri style?
    uri = 'spotify:playlist:40dcGwdCvUDFwS893qdaLd'  # modern uri

    hot_playlist(60, uri)

# remove all songs older than daysOldLimit from given playlist
# based on:
#  https://github.com/plamere/spotipy/blob/master/examples/remove_specific_tracks_from_playlist.py
#  https://github.com/plamere/spotipy/blob/master/examples/read_a_playlist.py
def hot_playlist(daysOldLimit, list_uri):
    # TODO: ensure this works with very long playlists (over 100 songs)
    playlist_id = list_uri.split(':')[2]
    results = sp.user_playlist(username, playlist_id)
    #print(json.dumps(results, indent=4))

    now = timeNowUTC()
    track_ids = [] # list of tracks to remove
    for index, item in enumerate(results["tracks"]["items"]):
        # calculate the time elapsed since track was added to playlist
        dateStr = item["added_at"] # e.g. "2019-11-12T04:21:15Z"
        if dateStr != None:
            addDate = parser.parse(dateStr) # magic date parser

            # get the delta time since playlist was added
            delta = relativedelta(now, addDate)
            print("age: ({}y, {}m, {}d), {}h:{}m:{}s \t --- #{} '{}'".format(delta.years, delta.months, delta.days, delta.hours, delta.minutes, delta.seconds, index, item["track"]["name"]))

        # TODO: account for if delta is 1 year, 1 hour (for example)
        #   https://dateutil.readthedocs.io/en/stable/relativedelta.html
        #if delta.hours > 1:
        # "added_at" will be null for very old playlists
        # TODO: for now just checking dummy condition
        if dateStr == None or index == 11:
            track_ids.append( { "uri" : item["track"]["id"], "positions": [ int(index)] } )
            #track_ids.append( { "uri" : item["track"]["name"], "positions": [ int(index)] } ) # TODO: for now use name for clarity in output

    print(json.dumps(track_ids, indent=4))
    print("deleting " + str(len(track_ids)) + " tracks")
    # remove desired tracks:
    sp.user_playlist_remove_specific_occurrences_of_tracks(username, playlist_id, track_ids)

# returns datetime for the UTC time now (location aware)
# (can be used for relativedelta calculations)
def timeNowUTC():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

if __name__ == "__main__":
    main()
