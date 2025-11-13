# Vauge instructions:

- Run song_logger.py to start logging songs 
- Songs and their info are saved to spotify_history.db (can safely delete the database to restart it[code will automatically remake it blank])
- Run interface.py to start hosting the visual interface (default on http://127.0.0.1:5500)
- To extend this to a online access interface, run: ngrok http 5500 --host-header="localhost:5500"
- Interface will now be available at the address given by the ngrok output
