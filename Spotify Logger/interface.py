from flask import Flask, render_template_string
import sqlite3
import datetime
import json
from datetime import timedelta

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Listening Analytics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --spotify-green: #1DB954;
            --spotify-black: #191414;
            --dark-gray: #282828;
            --light-gray: #b3b3b3;
            --card-bg: rgba(40, 40, 40, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #b3b3b3;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--spotify-black) 0%, #000000 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 40px 20px;
            line-height: 1.6;
            scroll-behavior: smooth;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--spotify-green) 0%, #1ed760 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .header p {
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 300;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 50px;
        }
        
        .stat-card {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(29, 185, 84, 0.2);
        }
        
        .now-playing-card {
            background: linear-gradient(135deg, var(--spotify-green) 0%, #1aa34a 100%);
            color: black;
        }
        
        .now-playing-card:hover {
            box-shadow: 0 10px 30px rgba(29, 185, 84, 0.4);
        }
        
        .nothing-playing-card {
            background: var(--card-bg);
            color: var(--text-secondary);
        }
        
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 15px;
        }
        
        .now-playing-card .stat-icon {
            color: black;
        }
        
        .stat-card h3 {
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .now-playing-card h3 {
            color: rgba(0, 0, 0, 0.8);
        }
        
        .stat-value {
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.2;
        }
        
        .now-playing-card .stat-value {
            color: black;
        }
        
        .now-playing-track {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 5px;
            color: black;
        }
        
        .now-playing-artist {
            font-size: 1.2rem;
            font-weight: 500;
            color: rgba(0, 0, 0, 0.8);
        }
        
        .progress-container {
            margin-top: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            height: 6px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: black;
            border-radius: 10px;
            transition: width 0.3s ease;
        }
        
        .chart-section {
            background: var(--card-bg);
            border-radius: 20px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 30px;
            scroll-margin-top: 20px;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .section-header h2 {
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .section-icon {
            font-size: 1.5rem;
            margin-right: 15px;
            color: var(--spotify-green);
        }
        
        .chart-controls {
            display: flex;
            gap: 10px;
        }
        
        .chart-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: var(--text-primary);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }
        
        .chart-btn.active {
            background: var(--spotify-green);
            color: black;
            border-color: var(--spotify-green);
        }
        
        .chart-btn:hover:not(.active) {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            width: 100%;
        }
        
        .recent-songs-section {
            background: var(--card-bg);
            border-radius: 20px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 30px;
        }
        
        .songs-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .songs-table thead {
            border-bottom: 2px solid var(--spotify-green);
        }
        
        .songs-table th {
            padding: 15px 20px;
            text-align: left;
            font-weight: 600;
            color: var(--spotify-green);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .songs-table td {
            padding: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            transition: background-color 0.2s ease;
        }
        
        .songs-table tbody tr:hover td {
            background-color: rgba(29, 185, 84, 0.1);
        }
        
        .track-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .track-artwork {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--spotify-green) 0%, #1ed760 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.2rem;
        }
        
        .track-details {
            display: flex;
            flex-direction: column;
        }
        
        .track-name {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .track-artist {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .genre-tag {
            background: rgba(29, 185, 84, 0.2);
            color: var(--spotify-green);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .timestamp {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .stat-value {
                font-size: 1.8rem;
            }
            
            .now-playing-track {
                font-size: 1.5rem;
            }
            
            .now-playing-artist {
                font-size: 1rem;
            }
            
            .chart-section,
            .recent-songs-section {
                padding: 20px;
            }
            
            .songs-table {
                display: block;
                overflow-x: auto;
            }
            
            .section-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .chart-controls {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Listening Journey</h1>
            <p>Your personal Spotify statistics from the past 7 days</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card" onclick="scrollToSection('time-breakdown')">
                <div class="stat-icon">⏱️</div>
                <h3>Total Listening Time</h3>
                <div class="stat-value">{{ total_time }} hours</div>
            </div>
            
            {% if now_playing %}
            <div class="stat-card now-playing-card" onclick="scrollToSection('recent-songs')">
                <div class="stat-icon">🎵</div>
                <h3>Now Playing</h3>
                <div class="now-playing-track">{{ now_playing.track_name }}</div>
                <div class="now-playing-artist">{{ now_playing.artist_name }}</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {{ now_playing.progress_percent }}%"></div>
                </div>
            </div>
            {% else %}
            <div class="stat-card nothing-playing-card">
                <div class="stat-icon">🔇</div>
                <h3>Now Playing</h3>
                <div class="stat-value">Nothing Playing</div>
            </div>
            {% endif %}
            
            <div class="stat-card">
                <div class="stat-icon">🔥</div>
                <h3>Top Track This Week</h3>
                <div class="stat-value">{{ top_song }}</div>
            </div>
        </div>
        
        <div class="recent-songs-section">
            <div class="section-header">
                <div style="display: flex; align-items: center;">
                    <div class="section-icon">🎧</div>
                    <h2>Recently Played Tracks</h2>
                </div>
            </div>
            
            <table class="songs-table">
                <thead>
                    <tr>
                        <th>Track</th>
                        <th>Album</th>
                        <th>Genre</th>
                        <th>Played At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in recent_songs %}
                    <tr>
                        <td>
                            <div class="track-info">
                                <div class="track-artwork">♪</div>
                                <div class="track-details">
                                    <div class="track-name">{{ row[2] }}</div>
                                    <div class="track-artist">{{ row[3] }}</div>
                                </div>
                            </div>
                        </td>
                        <td>{{ row[4] }}</td>
                        <td>
                            <span class="genre-tag">{{ row[7] or "Unknown" }}</span>
                        </td>
                        <td>
                            <span class="timestamp">{{ row[1] }}</span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Time Breakdown Section -->
        <div id="time-breakdown" class="chart-section">
            <div class="section-header">
                <div style="display: flex; align-items: center;">
                    <div class="section-icon">📊</div>
                    <h2>Listening Time Breakdown</h2>
                </div>
                <div class="chart-controls">
                    <button class="chart-btn active" onclick="switchTimeChart('hourly')">By Hour</button>
                    <button class="chart-btn" onclick="switchTimeChart('daily')">By Day</button>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="timeChart"></canvas>
            </div>
        </div>

        <!-- Genre Breakdown Section -->
        <div id="genre-breakdown" class="chart-section">
            <div class="section-header">
                <div style="display: flex; align-items: center;">
                    <div class="section-icon">🥧</div>
                    <h2>Genre Distribution</h2>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="genreChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        function scrollToSection(sectionId) {
            document.getElementById(sectionId).scrollIntoView({ 
                behavior: 'smooth' 
            });
        }

        // Time chart data from Flask
        const timeData = {
            hourly: {{ hourly_data | tojson }},
            daily: {{ daily_data | tojson }}
        };

        let currentTimeChartView = 'hourly';
        let timeChartInstance = null;
        let genreChartInstance = null;

        function switchTimeChart(view) {
            currentTimeChartView = view;
            
            // Update button states
            document.querySelectorAll('.chart-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            updateTimeChart();
        }

        function updateTimeChart() {
            const ctx = document.getElementById('timeChart').getContext('2d');
            const data = timeData[currentTimeChartView];
            
            if (timeChartInstance) {
                timeChartInstance.destroy();
            }

            const isHourly = currentTimeChartView === 'hourly';
            const labels = isHourly ? 
                Array.from({length: 24}, (_, i) => `${i}:00`) : 
                ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
            
            const backgroundColors = isHourly ? 
                data.map((_, index) => {
                    const hue = (index * 15) % 360;
                    return `hsla(${hue}, 70%, 50%, 0.8)`;
                }) :
                ['#1DB954', '#1ed760', '#1aa34a', '#25c75c', '#169c42', '#2bd467', '#0f8a38'];

            timeChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: isHourly ? 'Listening Time (hours)' : 'Listening Time (hours)',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderColor: backgroundColors.map(color => color.replace('0.8', '1')),
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: isHourly ? 'Listening Time by Hour of Day' : 'Listening Time by Day of Week',
                            color: '#ffffff',
                            font: {
                                size: 16
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#b3b3b3'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: '#b3b3b3'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            });
        }

        // Initialize genre chart
        function initGenreChart() {
            const ctx = document.getElementById('genreChart').getContext('2d');
            const genreData = {{ genre_distribution | tojson }};
            
            // Generate colors for the pie chart
            const backgroundColors = [
                '#1DB954', '#1ed760', '#ff6b6b', '#4ecdc4', '#45b7d1', 
                '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd'
            ];

            genreChartInstance = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: genreData.labels,
                    datasets: [{
                        data: genreData.values,
                        backgroundColor: backgroundColors,
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: '#ffffff',
                                padding: 20,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'Genre Distribution',
                            color: '#ffffff',
                            font: {
                                size: 16
                            }
                        }
                    }
                }
            });
        }

        // Initialize charts when page loads
        document.addEventListener('DOMContentLoaded', function() {
            updateTimeChart();
            initGenreChart();
        });
    </script>
</body>
</html>
"""

def get_past_week_data():
    conn = sqlite3.connect("spotify_history.db")
    cursor = conn.cursor()

    # Calculate time 7 days ago
    week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    # Get recent songs
    cursor.execute("""
        SELECT * FROM playback_history
        WHERE timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (week_ago,))
    recent_songs = cursor.fetchall()

    # Total time listened 
    cursor.execute("""
        SELECT SUM(duration) FROM playback_history
        WHERE timestamp >= ?
    """, (week_ago,))
    total_seconds = cursor.fetchone()[0] or 0
    total_time_hours = round(total_seconds / 3600, 2)

    # Most listened song
    cursor.execute("""
        SELECT track_name, artist_name, COUNT(*) as count FROM playback_history
        WHERE timestamp >= ?
        GROUP BY track_name, artist_name
        ORDER BY count DESC
        LIMIT 1
    """, (week_ago,))
    song_row = cursor.fetchone()
    top_song = f"{song_row[0]} by {song_row[1]}" if song_row else "Unknown"

    # Get hourly listening data (for the bar chart)
    cursor.execute("""
        SELECT strftime('%H', timestamp) as hour, 
               SUM(duration)/3600.0 as hours_listened
        FROM playback_history
        WHERE timestamp >= ?
        GROUP BY hour
        ORDER BY hour
    """, (week_ago,))
    hourly_results = cursor.fetchall()
    
    # Create hourly data array (0-23 hours)
    hourly_data = [0.0] * 24
    for hour, hours_listened in hourly_results:
        hourly_data[int(hour)] = round(hours_listened, 2)

    # Get daily listening data
    cursor.execute("""
        SELECT strftime('%w', timestamp) as day_of_week,
               SUM(duration)/3600.0 as hours_listened
        FROM playback_history
        WHERE timestamp >= ?
        GROUP BY day_of_week
        ORDER BY day_of_week
    """, (week_ago,))
    daily_results = cursor.fetchall()
    
    # Create daily data array (0-6 for Sunday-Saturday)
    daily_data = [0.0] * 7
    for day, hours_listened in daily_results:
        daily_data[int(day)] = round(hours_listened, 2)

    # Get genre distribution for pie chart
    cursor.execute("""
        SELECT genres, COUNT(*) as count 
        FROM playback_history
        WHERE timestamp >= ? AND genres IS NOT NULL AND genres != ''
        GROUP BY genres
        ORDER BY count DESC
        LIMIT 10
    """, (week_ago,))
    genre_results = cursor.fetchall()
    
    genre_labels = [row[0] for row in genre_results]
    genre_values = [row[1] for row in genre_results]

    # Get now playing information
    now_playing = None
    if recent_songs:
        most_recent_song = recent_songs[0]
        track_start = datetime.datetime.strptime(most_recent_song[1], "%Y-%m-%d %H:%M:%S")
        track_duration = most_recent_song[8]  # duration in seconds
        track_end = track_start + timedelta(seconds=track_duration)
        current_time = datetime.datetime.now()
        
        # Check if the song should still be playing
        if current_time <= track_end:
            elapsed = (current_time - track_start).total_seconds()
            progress_percent = min(100, (elapsed / track_duration) * 100)
            
            now_playing = {
                'track_name': most_recent_song[2],
                'artist_name': most_recent_song[3],
                'progress_percent': round(progress_percent, 1),
                'time_remaining': max(0, track_duration - elapsed)
            }

    conn.close()

    return {
        'total_time': total_time_hours,
        'top_song': top_song,
        'recent_songs': recent_songs,
        'hourly_data': hourly_data,
        'daily_data': daily_data,
        'genre_distribution': {
            'labels': genre_labels,
            'values': genre_values
        },
        'now_playing': now_playing
    }

@app.route('/')
def index():
    data = get_past_week_data()
    return render_template_string(HTML_TEMPLATE, **data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)