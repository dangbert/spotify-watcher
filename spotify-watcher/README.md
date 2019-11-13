## Setup
* Acquire a Spotify API key from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
* Install dependency [spotipy](https://github.com/plamere/spotipy)
````bash
sudo pip3 install spotipy
```

## Example Run:
````bash
# deletes given song at index 1 in playlist
source secret.env && ./decayingPlaylist.py dangbert 40dcGwdCvUDFwS893qdaLd 6ttsH99vfvkAPF3s1tIPqB,1
````

---
## Resources
* [spotipy documentation](https://spotipy.readthedocs.io/en/latest/)
* [spotipy examples](https://github.com/plamere/spotipy/tree/master/examples)
* [Spotify Web API Libraries List](https://developer.spotify.com/documentation/web-api/libraries/)

