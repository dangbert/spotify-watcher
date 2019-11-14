#!/usr/bin/env python3
# source secret.env before running this program!
#./hot_playlist.py dangbert 40 "spotify:playlist:40dcGwdCvUDFwS893qdaLd" --backup_uri "spotify:playlist:40dcGwdCvUDFwS893qdaLd"

import spotipy
import spotipy.util as util
#from spotipy.oauth2 import SpotifyClientCredentials

import pprint
import json
import sys
import argparse

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Removes all songs from given playlist older than max_age days then exits.')
    # TODO: look for way to get username from the playlist_uri?
    parser.add_argument('username', type=str, help='(string) username of spotify account owning the playlist.')
    parser.add_argument('max_days', type=int, help='(int) max number of days a song can be in the playlist before removal.')
    parser.add_argument('playlist_uri', type=str, help='(string) uri of spotify playlist to modify (e.g. "spotify:playlist:i0dcGw2CvUDFwx833UdaLf"')
    # (args starting with '--' are made optional)
    parser.add_argument('--backup_uri', type=str, help='(optional string) uri of spotify playlist to also add the songs removed from playlist_uri.')
    args = parser.parse_args()
    if len(sys.argv)==1:
        print("example usage:")
        print('  ./hot_playlist.py dangbert 40 "spotify:playlist:40dcGwdCvUDFwS893qdaLd" --backup_uri "spotify:playlist:40dcGwdCvUDFwS893qdaLd"\n')
        parser.print_help(sys.stderr)
        exit(1)

    # setup API
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(args.username, scope)
    if not token:
        print("Can't get Spotify API token for", args.username)
        exit(1)
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    # modify playlist
    hot_playlist(sp, args.username, args.max_days, args.playlist_uri, args.backup_uri)


# remove all songs older than max_days from given playlist:
#   (copy removed songs to backup_uri playlist if not None)
# based on:
#  https://github.com/plamere/spotipy/blob/master/examples/remove_specific_tracks_from_playlist.py
#  https://github.com/plamere/spotipy/blob/master/examples/read_a_playlist.py
def hot_playlist(sp, username, max_days, playlist_uri, backup_uri=None):
    # TODO: ensure this works with very long playlists (over 100 songs)
    playlist_id = playlist_uri.split(':')[2]
    results = sp.user_playlist(username, playlist_id)
    #print(json.dumps(results, indent=4))

    now = timeNowUTC()
    track_ids = [] # list of tracks to remove
    for index, item in enumerate(results["tracks"]["items"]):
        # calculate the time elapsed since track was added to playlist
        dateStr = item["added_at"] # e.g. "2019-11-12T04:21:15Z"
        if dateStr != None: # "added_at" can be null for very old playlists
            addDate = parser.parse(dateStr) # magic date parser

            # get the delta time since playlist was added
            delta = relativedelta(now, addDate)
            print("age: ({}y, {}m, {}d), {}h:{}m:{}s \t --- #{} '{}'".format(delta.years, delta.months, delta.days, delta.hours, delta.minutes, delta.seconds, index, item["track"]["name"]))

        # TODO: account for if delta is 1 year, 1 hour (for example)
        #   https://dateutil.readthedocs.io/en/stable/relativedelta.html
        #if delta.hours > 1:
        # TODO: for now just checking dummy condition
        if dateStr == None or index == 11:
            track_ids.append( { "uri" : item["track"]["id"], "positions": [ int(index)] } )
            #track_ids.append( { "uri" : item["track"]["name"], "positions": [ int(index)] } ) # TODO: for now use name for clarity in output

    print(json.dumps(track_ids, indent=4))
    exit(0)
    print("deleting " + str(len(track_ids)) + " tracks")
    # remove desired tracks:
    sp.user_playlist_remove_specific_occurrences_of_tracks(username, playlist_id, track_ids)

# returns datetime for the UTC time now (location aware)
# (can be used for relativedelta calculations)
def timeNowUTC():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

if __name__ == "__main__":
    main()
