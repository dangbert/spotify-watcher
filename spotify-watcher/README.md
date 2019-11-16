# spotify-watcher:
This directory contains code for creating "smart" spotify playlists by running a script to monitor desired playlists continously and apply desired changes (after a new song is added for example).

---
## Key Features:
* **hot_playlist.py** - playlist songs that were not added in the last X days are automatically removed (as songs are removed they are also added to a second playlist if desired).

## Future Features (not finished):
* **cool_artists** - tool for conveniently exploring later a cool artist that you just found.
  * When a new song is added to a given playlist, it will automatically be removed and the top X songs by that artists will automatically be appended to a second playlist of "cool artists".
* **auto_remove** - Batch auto-remove duplicate songs from a set of playlists.
* **live_queue** - simple way for people at a party to queue their own music from their phone.
  * when songs are added to a given (collaborative) playlist, they will be immediately removed and appended to the user's current queue.
  * API doesn't currently support queue operations but it may be possible to make a [hacky solution](https://github.com/spotify/web-api/issues/462#issuecomment-311466159)
* **reversed_playlist** - new songs added to playlist are automatically moved to the very top of the playlist (bope playlist)
* (all_spanish automatic set of playlists combiner)

## Setup:
* Acquire a Spotify API key from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
* Install dependency [spotipy](https://github.com/plamere/spotipy)
````bash
pip3 install spotipy python-dateutil pytz --user
```

## Example Run:
````bash
source secret.env
# deletes songs that have been in given playlist for over 14 days (and adds them to the backup playlist)
./hot_playlist.py dangbert 14 "spotify:playlist:40dcGwdCvUDFwS893qdaLe" --backup_uri spotify:playlist:5RkoGPrfNbgjK0qkJizt1O
```` 
---
## Resources:
* [spotipy documentation](https://spotipy.readthedocs.io/en/latest/)
* [spotipy examples](https://github.com/plamere/spotipy/tree/master/examples)
* [Spotify Web API Libraries List](https://developer.spotify.com/documentation/web-api/libraries/)

## See Also:
* [Smarter Playlists Website](http://playlistmachinery.com/index.html), [github](https://github.com/plamere/SmarterPlaylists)
