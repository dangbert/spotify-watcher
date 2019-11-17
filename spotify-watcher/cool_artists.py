#!/usr/bin/env python3
# source secret.env before running this program!
# command for testing:
#   ./cool_artists.py dangbert spotify:playlist:5RkoGPrfNbgjK0qkJizt1O ""

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


# TODO: consider putting this online (with a dumb simple UI)
#   user chooses source playlist from dropdown of their playlists or enters the URI
#   backend hosted on (Heroku), frontend on engbert.me, and sharing on reddit...
def main():
    # parse args
    parser = argparse.ArgumentParser(description='Gets the top songs of each unique artist in source playlist and adds them to the dest playlist.')
    # TODO: look for way to get username from the playlist_uri?
    parser.add_argument('username', type=str, help='(string) username of spotify account owning the playlist.')
    parser.add_argument('source_playlist_uri', type=str, help='(string) uri of spotify playlist to source names of artists from (e.g. "spotify:playlist:i0dcGw2CvUDFwx833UdaLf"')
    # (args starting with '--' are made optional)
    parser.add_argument('dest_playlist_uri', type=str, help='(string) uri of spotify playlist to add the top songs to by the artists found in the source playlist OR set to "" to create a new playlist')
    parser.add_argument('--delete_after', type=bool, default=True, help='(optional bool) set "false" to not modify the source playlist, set "true" to empty the source playlist afterwards (default "true")')
    parser.add_argument('--song_count', type=int, default=3, help='(optional int) number of top songs to get from each artist (default 3)')
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

    # modify playlist
    print("Running cool_artists: " + str(datetime.today()) + "\n")
    cool_artists(sp, args.username, args.source_playlist_uri, args.dest_playlist_uri, args.song_count)


# TODO: easy to make based on:
#   https://github.com/plamere/spotipy/blob/master/examples/show_artist_top_tracks.py
# create new playlist if dest_playlist_uri is ""
# TODO: delete duplicates afterwards as well...
def cool_artists(sp, username, source_playlist_uri, dest_playlist_uri, delete_after=True, song_count=3):
    pass

if __name__ == "__main__":
    main()
