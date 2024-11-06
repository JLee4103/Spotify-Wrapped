import requests
from django.conf import settings
import base64

def get_spotify_token():
    """Fetches an application-level access token for Spotify API requests."""
    url = 'https://accounts.spotify.com/api/token'
    auth_string = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_encoded}'
    }
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json().get('access_token')

def get_top_tracks(user_token, limit=10):
    """Fetches the user's top tracks."""
    url = f"https://api.spotify.com/v1/me/top/tracks?limit={limit}"
    headers = {'Authorization': f'Bearer {user_token}'}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    tracks = []
    for item in response.json().get('items', []):
        tracks.append({
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'album_image': item['album']['images'][0]['url'],
            'preview_url': item.get('preview_url'),  # May be None
            'estimated_listening_time': round(item['duration_ms'] / 1000 / 60, 2)
        })
    return tracks
