#!/usr/bin/env python3
# tools to help my other python programs

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

##########################################################
# removes all duplicate songs in the given Spotify playlist
# keepOldest: (bool) set false to preserve the duplicate that was most recently added to the playlist instead of the oldest
##########################################################
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

##########################################################
# based on:
#   https://github.com/plamere/spotipy/blob/master/examples/show_artist_top_tracks.py
#   https://spotipy.readthedocs.io/en/latest/#spotipy.client.Spotify.user_playlist_add_tracks
# create new playlist if dest_playlist_uri is ""
##########################################################
def cool_artists(sp, username, source_uri, dest_uri, copy_num=3, delete_after=False):
    if dest_uri == "":
        # TODO: create new playlist for user
        pass
    source_id = source_uri.split(':')[2]
    dest_id = dest_uri.split(':')[2]
    results = get_all_playlist_tracks(sp, username, source_id)
    #print(json.dumps(results, indent=4))

    visitedArtists = {} # uri's of artists already "visited" to find their top songs
    track_ids = [] # ids of tracks to add to dest playlist

    # traverse songs (backwards so songs at bottom of source playlist --> songs at top of dest playlist)
    for index, item in enumerate(reversed(results["tracks"]["items"])):
        # TODO: set limit for number of artists to consider from a single song??
        #       (or at least on the max number of songs to be added bc of that single song)
        for artist in item["track"]["artists"]:
            if artist["uri"] in visitedArtists:
                continue

            # get list of "Popular" songs from the artist
            top_response = sp.artist_top_tracks(artist["uri"])
            #print(json.dumps(top_response, indent=4))
            for popIndex, popItem in enumerate(top_response["tracks"]):
                if popIndex < copy_num:
                    track_ids.append(popItem["id"])
            visitedArtists[artist["uri"]] = True

    print("\n\nnum track_ids: " + str(len(track_ids)))

    #track_ids = [y for y in range(201)] # TODO: for practice
    #print("practicing on:\n" + str(track_ids))
    # handle when > 100 songs are to be added (and ensure track_id[0] ends at top of the playlist):
    while len(track_ids) > 0:
        if len(track_ids) > 100:
            tmp = track_ids[len(track_ids)-100:len(track_ids)]
            track_ids = track_ids[0:len(track_ids)-100]
        else:
            tmp = track_ids
            track_ids = []
        sp.user_playlist_add_tracks(username, dest_id, tmp, [[0] for x in tmp])

    # remove duplicates from dest playlist
    remove_duplicates(sp, username, dest_uri, keepOldest=True, verbose=False)
    # clear all songs in the source playlist
    if delete_after:
        remove_all_playlist_tracks(sp, username, source_uri)

##########################################################
# remove all songs older than max_days from given playlist:
#   (copy removed songs to backup_uri playlist if not None)
# based on:
#  https://github.com/plamere/spotipy/blob/master/examples/remove_specific_tracks_from_playlist.py
#  https://github.com/plamere/spotipy/blob/master/examples/read_a_playlist.py
# verifyChanges: if True then script will ask for confirmation before changing the playlist
##########################################################
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
            print("* removed songs will be added to the playlist: '" + sp.user_playlist(username, backup_id)["name"] + "' (and then all duplicates removed)")
        print("* after removal " + str(len(results["tracks"]["items"]) - len(track_ids)) + " song(s) will remain in playlist '" + results["name"] + "'")
    if not verifyChanges or input("\nRemove " + str(len(track_ids)) + " songs from playlist '" + results["name"] + "'? (y/n): " ).lower().strip() in ('y','yes'):
        runAgain = len(track_ids) > 100
        track_ids=track_ids[:100] # force length <= 100

        # add songs in track_ids to backup_uri playlist (only 100 can be added at once)
        if backup_uri != None:
            sp.user_playlist_add_tracks(username, backup_id, [obj["uri"] for obj in track_ids])
            if verbose:
                print("Appended the removed songs to backup playlist '" + sp.user_playlist(username, backup_id)["name"] + "'.")
            # TODO: consider only adding the songs that aren't already in backup playlist instead of this:
            # now remove duplicates from backup playlist
            remove_duplicates(sp, username, backup_uri, keepOldest=True, verbose=False)

        # now remove desired tracks (only can delete 100 at a time)
        sp.user_playlist_remove_specific_occurrences_of_tracks(username, playlist_id, track_ids)

        if runAgain: # recursively continue deleting the rest of the tracks
            hot_playlist(sp, username, max_days, playlist_uri, backup_uri, False)
    else:
        print("Aborting without modifying playlist.")

# remove all songs in a given playlist
def remove_all_playlist_tracks(sp, username, playlist_uri):
    # remove all songs that have been in the playlist for longer than 0 days
    hot_playlist(sp, username, 0, playlist_uri, backup_uri=None, verifyChanges=False)

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
