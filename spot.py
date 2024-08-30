import json
from collections import defaultdict

# Load data
with open('artist_log.json', 'r') as f:
    artist_data = [json.loads(line) for line in f]

with open('track_log.json', 'r') as f:
    track_data = [json.loads(line) for line in f]

# Define thresholds
POPULARITY_THRESHOLD = 50
FOLLOWER_THRESHOLD = 1000000
SONG_COUNT_THRESHOLD = 0

# Create dictionaries to store follower counts and track details
artist_followers = {}
track_count = defaultdict(int)
underrated_songs = []

# Populate artist followers
for artist in artist_data:
    artist_followers[artist['artist_id']] = artist['followers']

# Count track appearances
for track in track_data:
    track_count[track['track_id']] += 1

# Determine underrated songs
for track in track_data:
    if 'artist_id' not in track:
        print(f"Missing 'artist_id' in track data: {track}")
        continue
    
    artist_followers_count = artist_followers.get(track['artist_id'], 0)
    track_appearance_count = track_count.get(track['track_id'], 0)
    
    is_underrated = (
        track['popularity'] < POPULARITY_THRESHOLD and
        artist_followers_count < FOLLOWER_THRESHOLD and
        track_appearance_count > SONG_COUNT_THRESHOLD
    )
    
    print(f"Processing track: {track['track_name']} by {track['artist_name']}")
    print(f"Popularity: {track['popularity']}, Artist Followers: {artist_followers_count}, Track Count: {track_appearance_count}")
    print(f"Is underrated: {is_underrated}")

    if is_underrated:
        underrated_songs.append(track)

# Save underrated songs to JSON file
with open('underratedsongs.json', 'w') as f:
    json.dump(underrated_songs, f, indent=4)

print(f"Populated 'underratedsongs.json' with {len(underrated_songs)} underrated songs.")
