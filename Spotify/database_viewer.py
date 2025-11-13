import sqlite3
import pandas as pd

conn = sqlite3.connect("spotify_history.db")
df = pd.read_sql_query("SELECT * FROM playback_history", conn)
print(df)
conn.close()
