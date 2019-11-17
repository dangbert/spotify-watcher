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
from datetime import datetime

def main():
    # TODO: add arg that will generate a settings file for all my playlist so I can batch run this on all my playlists
    # parse args
    parser = argparse.ArgumentParser(description='Removes all duplicate songs in the given Spotify playlist. (Prompts confirmation before removal).')
    parser.add_argument('username', type=str, help='(string) username of spotify account owning the playlist.')
    parser.add_argument('playlist_uri', type=str, help='(string) uri of spotify playlist to modify (e.g. "spotify:playlist:i0dcGw2CvUDFwx833UdaLf"')
    # (args starting with '--' are made optional)
    parser.add_argument('--keep_oldest', type=str, default=True, help='(bool) set "false" to preserve the duplicate that was most recently added to the playlist instead of the oldest')
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

    # remove duplicates
    remove_duplicates(sp, args.username, args.playlist_uri, args.keep_oldest)

# removes all duplicate songs in the given Spotify playlist
# keepOldest: (bool) set false to preserve the duplicate that was most recently added to the playlist instead of the oldest
def remove_duplicates(sp, username, playlist_uri, keepOldest=True, verbose=True):
    if verbose:
        print("Running remove_duplicates: " + str(datetime.today()) + "\n")
    playlist_id = playlist_uri.split(':')[2]
#
    # get entire list of tracks in playlist
    results = get_all_playlist_tracks(sp, username, playlist_id)
    #print(json.dumps(results, indent=4))

    # TODO: use keepOldest (perhaps iterate the list backwards... but make sure index in track_ids is correct for removal)
    # TODO: need to use the date_added instead of index!!!!

    # search for duplicate songs, and mark the indices of the ones to be removed in deleteMap:
    deleteMap = {}     # indices of songs in here that are stored as True will all be deleted
    for index, item in enumerate(results["tracks"]["items"]):
        # if we have already labeled this song for keep/deletion then skip it
        if index in deleteMap:
            continue
        # compare to rest of items in playlist
        for index2, item2 in enumerate(results["tracks"]["items"]):
            if index == index2:
                continue
            if are_songs_duplicates(item, item2):
                deleteMap[index] = False # indicate we know it has a duplicate, but to keep this one
                deleteMap[index2] = True # mark the "other" one for deletion

    track_ids = [] # populate list of songs to remove
    # also print everything to be removed in order
    for index, item in enumerate(results["tracks"]["items"]):
        if index in deleteMap and deleteMap[index] == True:
            track_ids.append( { "uri" : item["track"]["id"], "positions": [index] } )
            if verbose:
                print("X\tindex: #{}, name: {}".format(index, item["track"]["name"]))
        elif verbose:
            print("\tindex: #{}, name: {}".format(index, item["track"]["name"]))

    if len(track_ids) == 0:
        if verbose:
            print("\n--------------\nNo duplicates to remove!")
        return
    if verbose:
        print("\n--------------")
        print("* after removal " + str(len(results["tracks"]["items"]) - len(track_ids)) + " song(s) will remain in playlist '" + results["name"] + "'")
    if not verbose or input("\nRemove " + str(len(track_ids)) + " songs from playlist '" + results["name"] + "'? (y/n): " ).lower().strip() in ('y','yes'):
        runAgain = len(track_ids) > 100

        track_ids=track_ids[:100] # force length <= 100
        sp.user_playlist_remove_specific_occurrences_of_tracks(username, playlist_id, track_ids)
        if runAgain: # recursively continue deleting the rest of the tracks
            remove_duplicates(sp, username, playlist_uri, keepOldest, False)
    else:
        print("Aborting without modifying playlist.")

# Returns true if songs are considered duplicates
def are_songs_duplicates(s1, s2):
    if s1['track']['id'] == s2['track']['id']:
        return True
    return False

if __name__ == "__main__":
    main()
