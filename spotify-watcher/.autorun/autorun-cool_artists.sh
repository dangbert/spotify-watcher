#!/bin/bash
# crontab settings:
#0  * * * * /home/pi/Downloads/RUN/misc-tools/spotify-watcher/autorun-cool_artists.sh
#15 * * * * /home/pi/Downloads/RUN/misc-tools/spotify-watcher/autorun-cool_artists.sh
#30 * * * * /home/pi/Downloads/RUN/misc-tools/spotify-watcher/autorun-cool_artists.sh
#45 * * * * /home/pi/Downloads/RUN/misc-tools/spotify-watcher/autorun-cool_artists.sh

NUM_COPY=5

BASE="/home/pi/Downloads/misc-tools/spotify-watcher/.autorun"
cd "$BASE"
source "secret.env"
source "playlists.env"

LOG="log--cool_artists.txt"

yes | ../cool_artists.py dangbert "$COOL_ARTISTS" "$PLAY_COOL_ARTISTS" --copy_num "$NUM_COPY" --delete_after True >>$LOG 2>&1
