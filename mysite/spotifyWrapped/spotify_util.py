import requests
import spotifyWrapped.settings


def get_spotify_wrapped_data(access_token, period='long_term', refresh_access_token_callback=None):
    """
    Fetches the user's top tracks and top artists from Spotify based on the selected time range.
    Optionally refreshes the access token if expired.
    """
    if not access_token:
        return [], []

    headers = {"Authorization": f"Bearer {access_token}"}

    # If the token is expired and there's a refresh callback, refresh the token
    if refresh_access_token_callback:
        access_token = refresh_access_token_callback()

    # Determine the correct time range
    time_range_map = {
        'Past Month': 'short_term',
        'Past 6 Months': 'medium_term',
        'Past Year': 'long_term'
    }
    time_range = time_range_map.get(period, 'long_term')

    # Fetch user's top tracks
    top_tracks_url = f"https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={time_range}"
    top_tracks_response = requests.get(top_tracks_url, headers=headers)
    
    top_tracks = []
    if top_tracks_response.status_code == 200:
        top_tracks_data = top_tracks_response.json().get('items', [])
        top_tracks = [
            {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track.get('preview_url')
            }
            for track in top_tracks_data
        ]
    else:
        print(f"Failed to fetch top tracks: {top_tracks_response.json()}")

    # Fetch user's top artists
    top_artists_url = f"https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}"
    top_artists_response = requests.get(top_artists_url, headers=headers)
    
    top_artists = []
    if top_artists_response.status_code == 200:
        top_artists_data = top_artists_response.json().get('items', [])
        top_artists = [
            {
                'name': artist['name'],
                'image': artist['images'][0]['url'] if artist['images'] else None,
            }
            for artist in top_artists_data
        ]
    else:
        print(f"Failed to fetch top artists: {top_artists_response.json()}")

    return top_tracks, top_artists
