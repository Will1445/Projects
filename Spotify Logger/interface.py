import sqlite3
import datetime
from datetime import timedelta
from flask import Flask, render_template

app = Flask(__name__)
 
def week_stats():
    conn = sqlite3.connect("spotify_history.db")
    cursor = conn.cursor()

    # past week
    past_week = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S") 

    # Most recent songs
    cursor.execute("""
        SELECT * FROM playback_history
        WHERE timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (past_week,)) 
    recent_songs = cursor.fetchall()

    # Total listening time 
    cursor.execute("""
        SELECT SUM(duration) FROM playback_history
        WHERE timestamp >= ?
    """, (past_week,)) 
    
    seconds = cursor.fetchone()[0] or 0 
    total_time = round(seconds / 3600, 2)

    # Most listened song
    cursor.execute("""
        SELECT track_name, artist_name, COUNT(*) as count FROM playback_history
        WHERE timestamp >= ?
        GROUP BY track_name, artist_name
        ORDER BY count DESC
        LIMIT 1
    """, (past_week,)) 
    song_row = cursor.fetchone() 
    top_song = f"{song_row[0]} by {song_row[1]}" if song_row else "Unknown"

    # Hourly listening data 
    cursor.execute("""
        SELECT strftime('%H', timestamp) as hour, 
               SUM(duration)/3600.0 as hours_listened
        FROM playback_history
        WHERE timestamp >= ?
        GROUP BY hour
        ORDER BY hour
    """, (past_week,))
    hourly = cursor.fetchall() 
     
    hourly_dist = [0.0] * 24 
    for hour, hours_listened in hourly:
        hourly_dist[int(hour)] = round(hours_listened, 2) 

    # Daily listening data
    cursor.execute("""
        SELECT strftime('%w', timestamp) as day_of_week,
               SUM(duration)/3600.0 as hours_listened
        FROM playback_history
        WHERE timestamp >= ?
        GROUP BY day_of_week
        ORDER BY day_of_week
    """, (past_week,)) 
    daily = cursor.fetchall() 
    
    daily_dist = [0.0] * 7
    for day, hours_listened in daily:
        daily_dist[int(day)] = round(hours_listened, 2)
 
    # Genre distribution
    cursor.execute("""
        SELECT genres, COUNT(*) as count 
        FROM playback_history
        WHERE timestamp >= ? AND genres IS NOT NULL AND genres != ''
        GROUP BY genres
        ORDER BY count DESC
        LIMIT 10
    """, (past_week,))
    genres = cursor.fetchall()
     
    genre_lab = [row[0] for row in genres]
    genre_val = [row[1] for row in genres]

    # Now playing  
    current = None
    if recent_songs:
        most_recent_song = recent_songs[0]
        track_start = datetime.datetime.strptime(most_recent_song[1], "%Y-%m-%d %H:%M:%S") 
        track_duration = most_recent_song[8]
        track_end = track_start + timedelta(seconds=track_duration)
        current_time = datetime.datetime.now()

        if current_time <= track_end:
            elapsed = (current_time - track_start).total_seconds() 
            progress_percent = min(100, (elapsed / track_duration) * 100)
            
            current = {
                'track_name': most_recent_song[2],
                'artist_name': most_recent_song[3],
                'progress_percent': round(progress_percent, 1),
                'time_remaining': max(0, track_duration - elapsed)
            }

    conn.close() 

    return {
        'total_time': total_time,
        'top_song': top_song,
        'recent_songs': recent_songs,
        'hourly_data': hourly_dist,
        'daily_data': daily_dist,
        'genre_distribution': {
            'labels': genre_lab,
            'values': genre_val
        },
        'now_playing': current
    }

@app.route('/')
def index():
    data = week_stats()
    return render_template("interface.html", **data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
    
