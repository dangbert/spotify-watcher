#!/bin/bash
# crontab 3AM every day:
#0 3 * * * /home/pi/Downloads/RUN/misc-tools/spotify-watcher/autorun-hot_playlist.sh
cd /home/pi/autorun-spotify
source secret.env
source playlists.env

LOG="./log--hot_playlist.txt"

# H playlists
yes | ./hot_playlist.py dangbert 60 "$H" --backup_uri "$H_ALL" >>$LOG 2>&1

# only keep recent cool artists
# (sleep 5 minutes first to prevent conflict with autorun-cool_artists.sh)
sleep $((5*60)) && yes | ./hot_playlist.py dangbert 60 "$PLAY_COOL_ARTISTS" --backup_uri "$PLAY_ALL_COOL_ARTISTS" >>$LOG 2>&1

# TODO: also create bope and recently bope
# TODO: make collaborative cool artists playlist?
