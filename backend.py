from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import spotipy
import time
import os

load_dotenv()

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri="http://127.0.0.1:8000/callback",
        scope="user-modify-playback-state user-read-playback-state"
    )
)

playback = sp.current_playback()
volume = playback["device"]["volume_percent"]
image_url = playback["item"]["album"]["images"][0]["url"]
last_cover = None


def search_for_song():
    result = sp.search(q="Stolen Dance - Remix", type="track", limit=1)

    track = result["tracks"]["items"][0]
    uri = track["uri"]

    sp.start_playback(uris=[uri])
    print("Playing:", track["name"])