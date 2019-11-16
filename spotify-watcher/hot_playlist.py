#!/usr/bin/env python3
# source secret.env before running this program!
# command for testing:
#   ./hot_playlist.py dangbert 1 "spotify:playlist:40dcGwdCvUDFwS893qdaLd" --backup_uri "spotify:playlist:5RkoGPrfNbgjK0qkJizt1O"

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
    parser = argparse.ArgumentParser(description='Removes all songs from given playlist older than max_age days then exits.  (Prompts confirmation before removal).')
    # TODO: look for way to get username from the playlist_uri?
    parser.add_argument('username', type=str, help='(string) username of spotify account owning the playlist.')
    parser.add_argument('max_days', type=int, help='(int) max number of days a song can be in the playlist before removal.')
    parser.add_argument('playlist_uri', type=str, help='(string) uri of spotify playlist to modify (e.g. "spotify:playlist:i0dcGw2CvUDFwx833UdaLf"')
    # (args starting with '--' are made optional)
    parser.add_argument('--backup_uri', type=str, help='(optional string) uri of spotify playlist to also add the songs removed from playlist_uri.')
    args = parser.parse_args()
    if len(sys.argv) == 1:
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

    print("Running: " + str(datetime.today()) + "\n")
    # modify playlist
    hot_playlist(sp, args.username, args.max_days, args.playlist_uri, args.backup_uri)

# remove all songs older than max_days from given playlist:
#   (copy removed songs to backup_uri playlist if not None)
# based on:
#  https://github.com/plamere/spotipy/blob/master/examples/remove_specific_tracks_from_playlist.py
#  https://github.com/plamere/spotipy/blob/master/examples/read_a_playlist.py
# verifyChanges: if True then script will ask for confirmation before changing the playlist
def hot_playlist(sp, username, max_days, playlist_uri, backup_uri=None, verifyChanges=True):
    verbose = verifyChanges # whether to print extra debug info
    playlist_id = playlist_uri.split(':')[2]
    results = get_all_playlist_tracks(sp, username, playlist_id)
    backup_id = None if (backup_uri == None) else backup_uri.split(':')[2]
    if verbose:
        print("playlist length: " + str(len(results['tracks']['items'])))
        print("(songs marked for deletion with 'X'):")

    now = timeNowUTC()
    track_ids = []
    # populate list of tracks to remove:
    for index, item in enumerate(results["tracks"]["items"]):
        # calculate the time elapsed since track was added to playlist
        dateStr = item["added_at"] # e.g. "2019-11-12T04:21:15Z"
        if dateStr != None:        # "added_at" can be null for very old playlists
            addDate = parser.parse(dateStr) # magic date parser

            # get the delta time since playlist was added
            delta = relativedelta(now, addDate)
            elapsedDays = (now - (now-delta)).days # (more magic) https://stackoverflow.com/a/43521106

        else:
            print("dateStr None for song " + item["track"]["name"])

        if dateStr == None or elapsedDays >= max_days:
            if verbose:
                print("X\tage: ({}y, {}m, {}d), {}h:{}m:{}s \t== {} days \t --- #{} '{}'".format(delta.years, delta.months, delta.days, delta.hours, delta.minutes, delta.seconds, elapsedDays, index, item["track"]["name"]))
            track_ids.append( { "uri" : item["track"]["id"], "positions": [ int(index)] } )
        else:
            print("\tage: ({}y, {}m, {}d), {}h:{}m:{}s \t== {} days \t --- #{} '{}'".format(delta.years, delta.months, delta.days, delta.hours, delta.minutes, delta.seconds, elapsedDays, index, item["track"]["name"]))

    if len(track_ids) == 0:
        if verbose:
            print("\n--------------\nNo songs ready to remove!")
        return
    if verbose:
        print("\n--------------")
        if backup_id != None:
            print("* removed songs will be added to the playlist: '" + sp.user_playlist(username, backup_id)["name"] + "'")
        print("* after removal " + str(len(results["tracks"]["items"]) - len(track_ids)) + " song(s) will remain in playlist '" + results["name"] + "'")
    if not verifyChanges or input("\nRemove " + str(len(track_ids)) + " songs from playlist '" + results["name"] + "'? (y/n): " ).lower().strip() in ('y','yes'):
        runAgain = len(track_ids) > 100
        track_ids=track_ids[:100] # force length <= 100

        # add songs in track_ids to backup_uri playlist (only 100 can be added at once)
        if backup_uri != None:
            sp.user_playlist_add_tracks(username, backup_id, [obj["uri"] for obj in track_ids])
            if verbose:
                print("Appended the removed songs to backup playlist '" + sp.user_playlist(username, backup_id)["name"] + "'.")
        # now remove desired tracks (only can delete 100 at a time)
        sp.user_playlist_remove_specific_occurrences_of_tracks(username, playlist_id, track_ids)

        if runAgain: # recursively continue deleting the rest of the tracks
            hot_playlist(sp, username, max_days, playlist_uri, backup_uri, False)
    else:
        print("Aborting without modifying playlist.")

# returns the json results for all the tracks in a playlist (even if > 100 songs)
def get_all_playlist_tracks(sp, username, playlist_id):
    results = sp.user_playlist(username, playlist_id)

    while results['tracks']['next']:
        # https://github.com/plamere/spotipy/issues/246#issuecomment-359128303
        #   note that tmpResults has exact same format as results['tracks']
        #   ._get is a workaround to issue with .next() being out of date
        tmpResults = sp._get(results['tracks']['next'])
        results['tracks']['items'].extend(list(tmpResults['items']))
        results['tracks']['next'] = tmpResults['next'] # update next value
    #print(json.dumps(results, indent=4))
    return results

# returns datetime object for the UTC time now (location aware)
# (can be used for relativedelta calculations)
def timeNowUTC():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

if __name__ == "__main__":
    main()
