import sqlite3
import datetime
from datetime import timedelta
from flask import Flask, render_template

app = Flask(__name__)

current_week = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S") 

def recent_songs(week):
    database = sqlite3.connect("spotify_history.db")
    cursor = database.cursor()
    
    cursor.execute("""
        SELECT * FROM playback_history
        WHERE timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT 5""" , (week,)) 
    
    recent_songs = cursor.fetchall()
    database.close()
    return recent_songs
    
    
def most_listened_song(week):
    database = sqlite3.connect("spotify_history.db")
    cursor = database.cursor()
    
    cursor.execute("""
        SELECT track_name, artist_name, COUNT(*) as count FROM playback_history
        WHERE timestamp >= ?
        GROUP BY track_name, artist_name
        ORDER BY count DESC
        LIMIT 1""", (week,)) 
    
    song = cursor.fetchone()
    song_format = f"{song[0]} by {song[1]}" if song else "Unknown"
    database.close()
    
    return song_format
    
    
def total_time(week):
    database = sqlite3.connect("spotify_history.db")
    cursor = database.cursor()
    
    cursor.execute("""
        SELECT SUM(duration) FROM playback_history
        WHERE timestamp >= ?""", (week,)) 
    
    total = round(cursor.fetchone()[0]/3600, 2)
    database.close()
    
    return total
    
    
def hourly_songs(week):
    database = sqlite3.connect("spotify_history.db")
    cursor = database.cursor()
    
    cursor.execute("""
        SELECT strftime('%H', timestamp) as hour, 
               SUM(duration)/3600.0 as hours_listened
        FROM playback_history
        WHERE timestamp >= ?
        GROUP BY hour
        ORDER BY hour""", (week,))
    
    songs_by_hour = cursor.fetchall()
    
    hourly_dist = [0.0] * 24 
    for hour, hours_listened in songs_by_hour:
        hourly_dist[int(hour)] = round(hours_listened, 2) 
    
    database.close()
    
    return hourly_dist
    
    
def daily_songs(week):
    database = sqlite3.connect("spotify_history.db")
    cursor = database.cursor()
    
    cursor.execute("""
        SELECT strftime('%w', timestamp) as day_of_week,
               SUM(duration)/3600.0 as hours_listened
        FROM playback_history
        WHERE timestamp >= ?
        GROUP BY day_of_week
        ORDER BY day_of_week""", (week,)) 
    
    songs_by_day = cursor.fetchall()
    
    daily_dist = [0.0] * 7
    for day, hours_listened in songs_by_day:
        daily_dist[int(day)] = round(hours_listened, 2)
        
    database.close()
    
    return daily_dist
    
def genres(week):
    database = sqlite3.connect("spotify_history.db")
    cursor = database.cursor()
    
    cursor.execute("""
        SELECT genres, COUNT(*) as count 
        FROM playback_history
        WHERE timestamp >= ? AND genres IS NOT NULL AND genres != ''
        GROUP BY genres
        ORDER BY count DESC
        LIMIT 10""", (week,))
    
    genres = cursor.fetchall()
    database.close()
    
    return genres
    
    
def current_song(week):
    current_time = datetime.datetime.now()
    recent_songs_list = recent_songs(week)
    current_song = recent_songs_list[0]
    
    current_song_duration = current_song[8]
    current_song_start = datetime.datetime.strptime(current_song[1], "%Y-%m-%d %H:%M:%S") 
    current_song_end = current_song_start + timedelta(seconds=current_song_duration)
    
    if current_time < current_song_end:
        time_played = (current_time - current_song_start).total_seconds()
        progress = (time_played/current_song_duration) * 100
        
        current = {
                'track_name': current_song[2],
                'artist_name': current_song[3],
                'progress_percent': round(progress, 1),
                'time_remaining': max(0, current_song_duration - time_played)
            }
        
        return current

    else:
        return None
        
    
@app.route('/')
def index():
    genres_list = genres(current_week)
    
    data = {
        'total_time': total_time(current_week),
        'top_song': most_listened_song(current_week),
        'recent_songs': recent_songs(current_week),
        'hourly_data': hourly_songs(current_week),
        'daily_data': daily_songs(current_week),
        'genre_distribution': {
            'labels': [row[0] for row in genres_list],
            'values': [row[1] for row in genres_list]
        },
        'now_playing': current_song(current_week)
    }
    
    return render_template("interface.html", **data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
