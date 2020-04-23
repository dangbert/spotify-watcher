#!/usr/bin/env python3
# this file loosely based on: https://github.com/stavlocker/SpotifyNoDupes
# ./remove_duplicates.py dangbert spotify:playlist:5RkoGPrfNbgjK0qkJizt1O
import spotipy
import spotipy.util as util
from tools import remove_duplicates

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

if __name__ == "__main__":
    main()
