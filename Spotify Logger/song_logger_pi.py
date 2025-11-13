import spotipy
import time
import sqlite3
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# --- Spotify Authentication ---
credentials = {}
with open("spotify_config.txt") as f:
    for line in f:
        key, value = line.strip().split("=", 1)
        credentials[key] = value

client_id = credentials["SPOTIPY_CLIENT_ID"]
client_secret = credentials["SPOTIPY_CLIENT_SECRET"]
redirect_uri = credentials["SPOTIPY_REDIRECT_URI"]
scope = "user-read-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
))

# Setup SQLite database 
conn = sqlite3.connect("spotify_history.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS playback_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    track_name TEXT,
    artist_name TEXT,
    album_name TEXT,
    track_id TEXT,
    popularity INTEGER,
    genres TEXT,
    duration REAL
)
""")
conn.commit()

# --- Track playback ---
last_track_id = None

try:
    while True:
        try:
            current = sp.current_playback()
        except Exception as e:
            print("Error fetching playback:", e)
            time.sleep(10)
            continue

        if current and current.get('item'):
            track = current['item']
            track_id = track['id']

            # Only log when the track changes
            if track_id != last_track_id:
                last_track_id = track_id

                artist = track['artists'][0]
                artist_name = artist['name']
                artist_id = artist['id']

                # Fetch genres for this artist
                try:
                    artist_info = sp.artist(artist_id)
                    genres = artist_info.get('genres', [])
                    print(genres)
                    genre_str = ', '.join(genres) if genres else 'Unknown'
                except Exception:
                    genre_str = 'Unknown'

                # Log track data
                name = track['name']
                album = track['album']['name']
                popularity = track.get('popularity', 0)
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                duration = track.get("duration_ms", 0) /1000.0

                cursor.execute("""
                    INSERT INTO playback_history (timestamp, track_name, artist_name, album_name, track_id, popularity, genres, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (timestamp, name, artist_name, album, track_id, popularity, genre_str, duration))
                conn.commit()

                print(f"[{timestamp}] Logged: {name} by {artist_name} (Genre: {genre_str})")

        else:
            print("Nothing is playing right now.")

        time.sleep(5)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    conn.close()
