from dotenv import load_dotenv
load_dotenv()
import os
import subprocess
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
def _get_spotify_client():
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET as environment variables or in a .env file.")
    auth_manager = SpotifyClientCredentials()
    return spotipy.Spotify(auth_manager=auth_manager)
def _get_artist_id(sp, artist_name):
    results = sp.search(q='artist:' + artist_name, type='artist', limit=1)
    artists = results.get('artists', {}).get('items', [])
    if not artists:
        raise ValueError(f"Artist '{artist_name}' not found.")
    return artists[0]['id']
def _get_all_artist_tracks(sp, artist_id):
    track_info = []
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
        album_info = sp.album(album_id)
        album_name = album_info['name']
        tracks = sp.album_tracks(album_id)
        for t in tracks['items']:
            track_info.append({
                "uri": t['uri'],
                "name": t['name'],
                "album": album_name
            })
    return track_info
def _play_track_librespot(username, password, track_uri, device_name="crackify-player", librespot_path="librespot"):
    cmd = [
        librespot_path,
        "--name", device_name,
        "--username", username,
        "--password", password,
        "--track", track_uri,
        "--quiet"
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.wait()
    except FileNotFoundError:
        print(f"[crackify] ERROR: librespot executable not found at '{librespot_path}'. Check your PATH or provide the correct path to librespot.exe.")
        raise
    except KeyboardInterrupt:
        proc.terminate()
        raise
def autostream(username, password, artist, librespot_path="librespot"):
    print(f"[crackify] Logging in and finding tracks for '{artist}'...")
    sp = _get_spotify_client()
    artist_id = _get_artist_id(sp, artist)
    tracks = _get_all_artist_tracks(sp, artist_id)
    if not tracks:
        print("[crackify] No tracks found.")
        return
    print(f"[crackify] Streaming {len(tracks)} tracks by '{artist}' (looping forever)...")
    try:
        while True:
            for track in tracks:
                song = track['name']
                album = track['album']
                uri = track['uri']
                print(f"[crackify] Now playing: {song} [{album}]")
                _play_track_librespot(username, password, uri, librespot_path=librespot_path)
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[crackify] Autostream stopped by user.")