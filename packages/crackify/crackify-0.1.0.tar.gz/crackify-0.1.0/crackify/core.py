import os
import subprocess
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
def _get_spotify_client():
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET as environment variables.")
    auth_manager = SpotifyClientCredentials()
    return spotipy.Spotify(auth_manager=auth_manager)
def _get_artist_id(sp, artist_name):
    results = sp.search(q='artist:' + artist_name, type='artist', limit=1)
    artists = results.get('artists', {}).get('items', [])
    if not artists:
        raise ValueError(f"Artist '{artist_name}' not found.")
    return artists[0]['id']
def _get_all_artist_tracks(sp, artist_id):
    track_uris = set()
    albums = []
    seen = set()
    results = sp.artist_albums(artist_id=artist_id, album_type="album,single", limit=50)
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    for album in albums:
        album_id = album['id']
        if album_id in seen:
            continue
        seen.add(album_id)
        tracks = sp.album_tracks(album_id)
        for t in tracks['items']:
            track_uris.add(t['uri'])
    return list(track_uris)
def _play_track_librespot(username, password, track_uri, device_name="crackify-player"):
    cmd = [
        "librespot",
        "--name", device_name,
        "--username", username,
        "--password", password,
        "--track", track_uri,
        "--quiet"
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        raise
def autostream(username, password, artist):
    print(f"[crackify] Logging in and finding tracks for '{artist}'...")
    sp = _get_spotify_client()
    artist_id = _get_artist_id(sp, artist)
    track_uris = _get_all_artist_tracks(sp, artist_id)
    if not track_uris:
        print("[crackify] No tracks found.")
        return
    print(f"[crackify] Streaming {len(track_uris)} tracks by '{artist}' (looping forever)...")
    try:
        while True:
            for uri in track_uris:
                print(f"[crackify] Now playing: {uri}")
                _play_track_librespot(username, password, uri)
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[crackify] Autostream stopped by user.")