#!/usr/bin/env python3
# source secret.env before running this program!
# command for testing:
#   ./cool_artists.py dangbert spotify:playlist:5RkoGPrfNbgjK0qkJizt1O ""
#
# name this one: "somone is always the DJ"
# whenever people want to use it, they log into my site and enable it (by giving permissions and also pressing a button)
# then one of their playlists will be "activated" to make it

import spotipy
import spotipy.util as util
from tools import live_queue

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
    parser = argparse.ArgumentParser(description='Test live queue.')
    parser.add_argument('username', type=str, help='(string) username of spotify account owning the playlist.')
    args = parser.parse_args()

    # setup API
    scope = 'user-modify-playback-state' # TODO: possible to chain multiple scopes?
    token = util.prompt_for_user_token(args.username, scope)
    if not token:
        print("Can't get Spotify API token for", args.username)
        exit(1)
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    # modify playlist
    print("\nRunning live_queue: " + str(datetime.today()) + "\n")
    live_queue(sp, args.username)


if __name__ == "__main__":
    main()
