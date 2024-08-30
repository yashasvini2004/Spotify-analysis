import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse

# Spotify API credentials
client_id = "d20c2bc7f044402792d5759c7bdd2d12"
client_secret = "f61db7c8dbe3403b9670e53d3e3c0bc7"
redirect_uri = "http://localhost:8888/callback"
scope = "user-read-playback-state"

# Set up authorization
sp_oauth = SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri=redirect_uri,
                        scope=scope)

# Define a simple HTTP server to handle the redirect
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse.urlparse(self.path).query
        params = urlparse.parse_qs(query)
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Authorization successful. You can close this window.')
        else:
            self.send_response(400)
            self.end_headers()

def start_server():
    server_address = ('', 8888)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Starting HTTP server for authorization...')
    httpd.handle_request()
    return httpd.auth_code

def get_token():
    # Get the authorization URL
    auth_url = sp_oauth.get_authorize_url()
    print(f"Please authorize the application by visiting this URL: {auth_url}")

    # Open the authorization URL in the default web browser
    webbrowser.open(auth_url)

    # Start the HTTP server to capture the authorization code
    auth_code = start_server()

    # Get access token using the authorization code
    token_info = sp_oauth.get_access_token(auth_code)
    return token_info['access_token']

def log_current_track():
    access_token = get_token()
    sp = spotipy.Spotify(auth=access_token)

    while True:
        try:
            current_track = sp.current_playback()
            if current_track and current_track['is_playing']:
                track_id = current_track['item']['id']
                track_name = current_track['item']['name']
                album_name = current_track['item']['album']['name']
                album_id = current_track['item']['album']['id']
                artist_name = current_track['item']['artists'][0]['name']
                artist_id = current_track['item']['artists'][0]['id']
                popularity = current_track['item']['popularity']

                # Save track info to a file
                with open('track_log.json', 'a') as f:
                    log_entry = {
                        'track_id': track_id,
                        'track_name': track_name,
                        'album_name': album_name,
                        'artist_name': artist_name,
                        'artist_id': artist_id,  # Include artist_id
                        'popularity': popularity,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    json.dump(log_entry, f)
                    f.write('\n')
                
                print(f"Logged track: {track_name} by {artist_name} with popularity {popularity}")

                # Fetch artist details
                artist = sp.artist(artist_id)
                followers = artist['followers']['total']

                # Save artist info to a file
                with open('artist_log.json', 'a') as f:
                    artist_entry = {
                        'artist_id': artist_id,
                        'artist_name': artist_name,
                        'track_name': track_name,
                        'followers': followers,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    json.dump(artist_entry, f)
                    f.write('\n')

                print(f"Logged artist: {artist_name} with {followers} followers")

                # Fetch album details
                album = sp.album(album_id)
                album_name = album['name']
                album_release_date = album['release_date']
                featured_artists = album['artists']

                # Collect details for each featured artist
                featured_artists_details = []
                for artist in featured_artists:
                    artist_id = artist['id']
                    artist_name = artist['name']
                    artist_info = sp.artist(artist_id)
                    followers_count = artist_info['followers']['total']
                    
                    featured_artists_details.append({
                        'artist_id': artist_id,
                        'artist_name': artist_name,
                        'followers': followers_count
                    })

                # Save album and featured artists info to a file
                with open('album_log.json', 'a') as f:
                    album_entry = {
                        'album_name': album_name,
                        'album_id': album_id,
                        'release_date': album_release_date,
                        'featured_artists': featured_artists_details,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    json.dump(album_entry, f)
                    f.write('\n')

                print(f"Logged album: {album_name} with featured artists details")

            else:
                print("No track is currently playing.")

        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(6)  # Check every 1 minute

if __name__ == "__main__":
    log_current_track()
