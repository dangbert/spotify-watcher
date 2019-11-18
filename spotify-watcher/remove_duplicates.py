#!/usr/bin/env python3
# this file loosely based on: https://github.com/stavlocker/SpotifyNoDupes
# ./remove_duplicates.py dangbert spotify:playlist:5RkoGPrfNbgjK0qkJizt1O
import spotipy
import spotipy.util as util
# TODO: create a tools.py with common functions?
from hot_playlist import get_all_playlist_tracks

import pprint
import argparse
import sys
import json

from dateutil import parser
from dateutil.relativedelta import *
from datetime import datetime
import pytz


def main():
    # TODO: add arg that will generate a settings file for all my playlist so I can batch run this on all my playlists (in a shell script)
    # parse args
    parser = argparse.ArgumentParser(description='Removes all duplicate songs in the given Spotify playlist. (Prompts confirmation before removal).')
    parser.add_argument('username', type=str, help='(string) username of spotify account owning the playlist.')
    parser.add_argument('playlist_uri', type=str, help='(string) uri of spotify playlist to modify (e.g. "spotify:playlist:i0dcGw2CvUDFwx833UdaLf"')
    # (args starting with '--' are made optional)
    parser.add_argument('--keep_oldest', type=str, default='true', help='(string) set "false" to preserve the duplicate that was most recently added to the playlist instead of the oldest')
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args.keep_oldest = args.keep_oldest.lower()
    if args.keep_oldest not in ["true", "false"]:
        print("ERROR: argument for --keep_oldest must be 'true' or 'false'")
        exit(1)
    args.keep_oldest = True if args.keep_oldest == "true" else False

    # setup API
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(args.username, scope)
    if not token:
        print("Can't get Spotify API token for", args.username)
        exit(1)
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    # remove duplicates
    remove_duplicates(sp, args.username, args.playlist_uri, args.keep_oldest)

# removes all duplicate songs in the given Spotify playlist
# keepOldest: (bool) set false to preserve the duplicate that was most recently added to the playlist instead of the oldest
def remove_duplicates(sp, username, playlist_uri, keepOldest=True, verbose=True):
    if verbose:
        print("Running remove_duplicates: " + str(datetime.today()) + "\n")
    playlist_id = playlist_uri.split(':')[2]
    # get entire list of tracks in playlist
    results = get_all_playlist_tracks(sp, username, playlist_id)
    #print(json.dumps(results, indent=4))

    # search for duplicate songs
    dupMap = {}     # maps track ids to list of indices of their occurences
    for index, item in enumerate(results["tracks"]["items"]):
        if not item['track']['id'] in dupMap:
            dupMap[item['track']['id']] = []
        dupMap[item['track']['id']].append(index)

    # for each set of duplicates, pick the song that is oldest/newest to the playlist to keep (based on keepOldest)
    deleteList = []  # indices to remove
    protectList = [] # indices to protect (don't delete even if its in deleteList)
    for track_id in dupMap:
        arr = dupMap[track_id] # list of indices of duplicate songs of track_id
        if len(arr) <= 1:      # no duplicates of this song
            continue
        deleteList.extend(arr)
        # now put one song in protectList (the version of this duplicate to keep)
        ageList = [0 for x in arr]
        for i, itemsIndex in enumerate(arr):
            # convert date to epoch seconds (magic date parser)
            dateStr = results["tracks"]["items"][itemsIndex]["added_at"] # e.g. "2019-11-12T04:21:15Z"
            ageList[i] = 0 if dateStr == None else int(parser.parse(dateStr).timestamp())
        oldest = ageList.index(min(ageList))
        newest = ageList.index(max(ageList))
        protectList.append(arr[oldest] if keepOldest else arr[newest])

    remove_list = []  # populate (properly formatted) list of songs to remove
    # also print everything to be removed in order
    for index, item in enumerate(results["tracks"]["items"]):
        if index in deleteList and not index in protectList:
            remove_list.append( { "uri" : item["track"]["id"], "positions": [index] } )
            if verbose:
                print("X\tindex: #{}, name: {}".format(index, item["track"]["name"]))
        elif verbose:
            print("\tindex: #{}, name: {}".format(index, item["track"]["name"]))

    # print info and do the delete with the user's confirmation
    if len(remove_list) == 0:
        if verbose:
            print("\n--------------\nNo duplicates to remove!")
        return
    if verbose:
        print("\n--------------")
        print("* after removal " + str(len(results["tracks"]["items"]) - len(remove_list)) + " song(s) will remain in playlist '" + results["name"] + "'")
    if not verbose or input("\nRemove " + str(len(remove_list)) + " songs from playlist '" + results["name"] + "'? (y/n): " ).lower().strip() in ('y','yes'):
        runAgain = len(remove_list) > 100

        remove_list=remove_list[:100] # force length <= 100
        sp.user_playlist_remove_specific_occurrences_of_tracks(username, playlist_id, remove_list)
        if runAgain: # recursively continue deleting the rest of the tracks
            remove_duplicates(sp, username, playlist_uri, keepOldest, False)
    else:
        print("Aborting without modifying playlist.")

if __name__ == "__main__":
    main()
