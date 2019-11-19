#!/usr/bin/env python3
# source secret.env before running this program!
# command for testing:
#   ./cool_artists.py dangbert spotify:playlist:5RkoGPrfNbgjK0qkJizt1O ""

import spotipy
import spotipy.util as util
from tools import cool_artists

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
    parser.add_argument('--delete_after', type=bool, default='false', help='(optional bool) set "true" to delete songs in the source playlist as well. (default "false")')
    parser.add_argument('--copy_num', type=int, default=3, help='(optional int) max number of top songs to add from each artist (default 3)')
    #parser.add_argument('--delete_after', type=str, default='true', help='(optional bool) set "false" to prevent deletion of songs in source playlist (default true)')
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)
    args.delete_after = args.delete_after.lower()
    if args.delete_after not in ["true", "false"]:
        print("ERROR: argument for --delete_after must be 'true' or 'false'")
        exit(1)
    args.delete_after = True if args.delete_after == "true" else False

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
    cool_artists(sp, args.username, args.source_playlist_uri, args.dest_playlist_uri, args.copy_num, args.delete_after)


if __name__ == "__main__":
    main()
