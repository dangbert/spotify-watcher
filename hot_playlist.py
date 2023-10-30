#!/usr/bin/env python3
# source secret.env before running this program!
# command for testing:
#   ./hot_playlist.py dangbert 1 "spotify:playlist:40dcGwdCvUDFwS893qdaLd" --backup_uri "spotify:playlist:5RkoGPrfNbgjK0qkJizt1O"

from tools import hot_playlist
import spotipy
import spotipy.util as util

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
    scope = 'playlist-modify-public playlist-modify-private'
    token = util.prompt_for_user_token(args.username, scope)
    if not token:
        print("Can't get Spotify API token for", args.username)
        exit(1)
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    print("\nRunning hot_playlist: " + str(datetime.today()) + "\n")
    # modify playlist
    hot_playlist(sp, args.username, args.max_days, args.playlist_uri, args.backup_uri)

if __name__ == "__main__":
    main()
