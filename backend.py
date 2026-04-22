from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import spotipy
import socket
import threading
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
volume = playback["device"]["volume_percent"] if playback else 50
last_cover = None

def skip_track():
    try:
        sp.next_track()
        print("[Spotify] Skip")
    except Exception as e:
        print(f"[Spotify] Skip error: {e}")
def previous_track():
    try:
        sp.previous_track()
        print("[Spotify] Back")
    except Exception as e:
        print(f"[Spotify] Back error: {e}")
def toggle_pause():
    try:
        pb = sp.current_playback()
        if pb is None:
            print("[Spotify] No active playback")
            return
        if pb["is_playing"]:
            sp.pause_playback()
            print("[Spotify] Paused")
        else:
            sp.start_playback()
            print("[Spotify] Resumed")
    except Exception as e:
        print(f"[Spotify] Pause error: {e}")
#// ====== ANPASSEN ======
SOCKET_HOST = "<IP_ADDR>"
SOCKET_PORT = 4444
#// ======================
def handle_event(msg: str):
    parts = msg.split(":")
    if parts[0] == "HELLO":
        print(f"[Socket] Hello from {parts[1] if len(parts) > 1 else '?'}")
        return
    if parts[0] != "BTN":
        print(f"[Socket] Unknown: {msg}")
        return

    if parts[1] in ("NEXT", "BACK"):
        print(f"[Socket] Menu nav: {parts[1]}")
        return

    if parts[1] == "SELECT" and len(parts) > 2:
        action = parts[2]
        if action == "Skip":
            skip_track()
        elif action == "Back":
            previous_track()
        elif action == "Pause":
            toggle_pause()
        else:
            print(f"[Socket] Unknown select: {action}")
def _client_thread(conn, addr):
    print(f"[Socket] Connected: {addr}")
    buf = b""
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                msg = line.decode(errors="ignore").strip()
                if msg:
                    handle_event(msg)
    except Exception as e:
        print(f"[Socket] Error {addr}: {e}")
    finally:
        print(f"[Socket] Disconnected: {addr}")
        conn.close()
def _server_thread():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SOCKET_HOST, SOCKET_PORT))
    s.listen(5)
    print(f"[Socket] Listening on {SOCKET_HOST}:{SOCKET_PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=_client_thread, args=(conn, addr), daemon=True).start()
def start_socket_server():
    t = threading.Thread(target=_server_thread, daemon=True)
    t.start()
def search_for_song():
    result = sp.search(q="Stolen Dance - Remix", type="track", limit=1)
    track = result["tracks"]["items"][0]
    uri = track["uri"]
    sp.start_playback(uris=[uri])
    print("Playing:", track["name"])

start_socket_server()
