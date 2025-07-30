from dotenv import load_dotenv
import os
import crackify
load_dotenv()

print("SPOTIPY_CLIENT_ID:", os.environ.get("SPOTIPY_CLIENT_ID"))
print("SPOTIPY_CLIENT_SECRET:", os.environ.get("SPOTIPY_CLIENT_SECRET"))

crackify.autostream(
    username="cobi5239@gmail.com",      # your actual Spotify login email
    password="Bobthedingdong101$",   # your actual Spotify password
    artist="LilRaffe"                  # or any artist
)