#!/bin/bash
# crontab settings (3:05AM every day):
# 5 3 * * *  /home/pi/Downloads/misc-tools/spotify-watcher/.autorun/autorun-hot_playlist.sh

BASE="/home/pi/Downloads/misc-tools/spotify-watcher/.autorun"
cd "$BASE"
source "secret.env"
source "playlists.env"

LOG="./log--hot_playlist.txt"

# H playlists
yes | ../hot_playlist.py dangbert 90 "$H" --backup_uri "$H_ALL" >>$LOG 2>&1

# only keep recent cool artists
yes | ../hot_playlist.py dangbert 90 "$PLAY_COOL_ARTISTS" --backup_uri "$PLAY_ALL_COOL_ARTISTS" >>$LOG 2>&1

# TODO: also create bope and recently bope
# TODO: make collaborative cool artists playlist?
