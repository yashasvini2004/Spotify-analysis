from flask import Flask, redirect, request, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key
app.config['SESSION_COOKIE_SECURE'] = True

# Your Spotify credentials
CLIENT_ID = 'd20c2bc7f044402792d5759c7bdd2d12'
CLIENT_SECRET = 'f61db7c8dbe3403b9670e53d3e3c0bc7'
REDIRECT_URI = 'http://localhost:8888/callback'

# Set up Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope='user-library-read user-read-playback-state user-modify-playback-state'
))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp.auth_manager.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp.auth_manager.get_access_token(request.args.get('code'))
    return redirect(url_for('show_songs'))

@app.route('/show-songs')
def show_songs():
    # Example code to load and display songs
    try:
        with open('underratedsongs.json') as f:
            songs = json.load(f)
    except FileNotFoundError:
        songs = []
    return render_template('songs.html', songs=songs)

@app.route('/play-track/<track_id>')
def play_track(track_id):
    # Example code to play a track
    sp.start_playback(uris=[f'spotify:track:{track_id}'])
    return redirect(url_for('show_songs'))

if __name__ == '__main__':
    app.run(debug=True, port=8888)
