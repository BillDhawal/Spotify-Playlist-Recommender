from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")



def get_playlists_by_keywords(keywords, limit_per_keyword=50, total_limit=500):
    """
    Retrieves a broad selection of playlists by querying multiple keywords.

    Parameters:
    - keywords (list of str): Keywords to search for playlists.
    - limit_per_keyword (int): Number of playlists to retrieve per keyword query.
    - total_limit (int): Total number of playlists to retrieve across all keywords.

    Returns:
    - DataFrame: A DataFrame containing the playlists' metadata.
    """
    all_playlists = []
    total_retrieved = 0

    for keyword in keywords:
        offset = 0
        while total_retrieved < total_limit:
            # Perform a search for playlists with the given keyword
            results = sp.search(q=keyword, type='playlist', limit=limit_per_keyword, offset=offset)
            playlists = results['playlists']['items']

            # Add playlists to the list and increment counters
            for playlist in playlists:
                all_playlists.append({
                    'playlist_name': playlist['name'],
                    'description': playlist['description'],
                    'playlist_id': playlist['id'],
                    'owner': playlist['owner']['display_name'],
                    'total_tracks': playlist['tracks']['total'],
                    'image_url': playlist['images'][0]['url'] if playlist['images'] else None,
                    'external_url': playlist['external_urls']['spotify']
                })
                total_retrieved += 1

                if total_retrieved >= total_limit:
                    break

            # Update the offset to retrieve the next batch
            offset += limit_per_keyword

            # Stop if there are no more results for the keyword
            if len(playlists) < limit_per_keyword:
                break

    # Convert the list of playlists to a DataFrame
    return pd.DataFrame(all_playlists)



def playlists_to_dataframe(playlists):
    """
    Converts a list of playlist metadata into a DataFrame.

    Args:
    playlists (list): A list of playlist dictionaries (or JSON strings) containing playlist information.

    Returns:
    pd.DataFrame: A DataFrame with columns: 'playlist_name', 'description', 'playlist_id', 'total_tracks', 'owner', and 'image_url'.
    """
    data = []

    for playlist in playlists:
        # If the playlist data is in JSON string format, convert it to a dictionary
        if isinstance(playlist, str):
            playlist = json.loads(playlist)

        # Extract fields from each playlist
        playlist_name = playlist.get("name")
        description = playlist.get("description")
        playlist_id = playlist.get("id")
        total_tracks = playlist.get("tracks", {}).get("total")
        owner = playlist.get("owner", {}).get("display_name")
        image_url = playlist.get("images", [{}])[0].get("url") if playlist.get("images") else None

        # Append the data to the list
        data.append({
            "playlist_name": playlist_name,
            "description": description,
            "playlist_id": playlist_id,
            "total_tracks": total_tracks,
            "owner": owner,
            "image_url": image_url
        })

    # Create DataFrame
    playlist_df = pd.DataFrame(data)
    return playlist_df


# Function to extract and print playlist details
def display_playlists(playlists):
    for playlist in playlists:
        name = playlist.get('name', 'No Name')
        description = playlist.get('description', 'No Description')
        spotify_link = playlist.get('external_urls', {}).get('spotify', 'No Link')
        image_url = playlist.get('images', [{}])[0].get('url', 'No Image URL')
        track_count = playlist.get('tracks', {}).get('total', 'Unknown')
        playlist_id = playlist.get('id')
        print(f"Playlist ID: {playlist_id}")
        print(f"Playlist Name: {name}")
        print(f"Description: {description}")
        print(f"Spotify Link: {spotify_link}")
        print(f"Image URL: {image_url}")
        print(f"Total Tracks: {track_count}")

        print("-" * 40)

def get_playlist_tracks(playlist_id):
    """
    Retrieve all tracks in a Spotify playlist and return as a DataFrame.

    Args:
    playlist_id (str): The Spotify playlist ID.

    Returns:
    pd.DataFrame: DataFrame containing track name, artist name, genre (if available), and description.
    """
    tracks = []
    results = sp.playlist_items(playlist_id)
    #results = sp.playlist_items(playlist_id, limit=100)

    # Loop to fetch all pages of playlist tracks
    while results:
        for item in results['items']:
            track = item.get('track')
            if track:  # Check if track is not None
                track_name = track.get('name')
                artist_name = track['artists'][0]['name'] if track.get('artists') else None
                genre = None  # Spotify API does not provide genre in playlist data
                description = f"{artist_name} - {track_name}" if artist_name and track_name else None
                tracks.append(
                    {'track_name': track_name, 'artist_name': artist_name, 'genre': genre, 'description': description}
                )

        # Check if there is a next page of results
        results = sp.next(results) if results.get('next') else None

    # Convert list to DataFrame
    playlist_df = pd.DataFrame(tracks)
    return playlist_df

# Function to combine all tracks from multiple playlists
def get_all_tracks_from_playlists(playlist_df):
    all_tracks = []  # List to hold DataFrames of tracks from each playlist

    # Iterate over each playlist in the DataFrame
    for _, row in playlist_df.iterrows():
        playlist_id = row['playlist_id']

        # Get the tracks for the current playlist
        tracks_df = get_playlist_tracks(playlist_id)

        # Add playlist metadata to each track entry
        tracks_df['playlist_name'] = row['playlist_name']
        tracks_df['playlist_id'] = playlist_id
        tracks_df['owner'] = row['owner']

        # Append to the list of all tracks
        all_tracks.append(tracks_df)

    # Concatenate all track DataFrames into one
    combined_tracks_df = pd.concat(all_tracks, ignore_index=True)
    return combined_tracks_df


def save_tracks_to_csv(all_tracks_df, filename="all_tracks.csv"):
    """
    Saves the combined tracks DataFrame to a CSV file.

    Parameters:
    - all_tracks_df (pd.DataFrame): The DataFrame containing all tracks with playlist metadata.
    - filename (str): The name of the CSV file to save to. Default is 'all_tracks.csv'.
    """
    try:
        all_tracks_df.to_csv(filename, index=False)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")


# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
#                                                            client_secret=CLIENT_SECRET))

# Example of retrieving playlists
# results = sp.search(q='chill' , type='playlist', limit=10)
# playlists = results['playlists']['items']
#
# Spotify Authentication
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret, requests_timeout=30)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Define a list of keywords for diverse playlist search
keywords = ["chill", "workout", "party", "classical", "jazz", "rock", "pop", "study", "sleep", "focus"]

# keywords = ["chill"]
# Retrieve playlists and save them to a DataFrame
playlists_df = get_playlists_by_keywords(keywords, limit_per_keyword=20, total_limit=500)


#
# playlist_df = playlists_to_dataframe(playlists)


# print(playlist_df.info())
# get_playlist_tracks(playlist_df)
# Example usage:
# Assuming playlist_df is your initial DataFrame with playlists
all_tracks_df = get_all_tracks_from_playlists(playlists_df)
save_tracks_to_csv(all_tracks_df, "chill_tracks.csv")


# # Example usage with a playlist ID
# playlist_id = '19PgP2QSGPcm6Ve8VhbtpG'  # Replace with the desired Spotify playlist ID
# playlist_df = get_playlist_tracks(playlist_id)
# print(playlist_df)







# Function to create a DATA FRAME , of playlist with its details.


