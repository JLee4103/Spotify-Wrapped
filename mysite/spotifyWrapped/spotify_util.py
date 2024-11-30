#import anthropic
import requests
from spotifyWrapped.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, ANTHROPIC_API_KEY
import os

def make_spotify_request(url, headers):
    """
    Helper function to make a GET request to Spotify API with error handling.
    Returns the response JSON if successful, otherwise logs and returns None.
    """
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: {response.json()}")
    except Exception as e:
        print(f"Error during API request: {e}")
    return None


def get_spotify_wrapped_data(access_token, period='long_term', refresh_access_token_callback=None):
    """
    Fetches the user's top tracks and top artists based on the selected time range.
    Optionally refreshes the access token if expired.
    """
    if not access_token:
        return [], []

    headers = {"Authorization": f"Bearer {access_token}"}

    if refresh_access_token_callback:
        access_token = refresh_access_token_callback()

    time_range = {
        'Past Month': 'short_term',
        'Past 6 Months': 'medium_term',
        'Past Year': 'long_term'
    }.get(period, 'long_term')

    top_tracks_url = f"https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={time_range}"
    top_artists_url = f"https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}"

    top_tracks_data = make_spotify_request(top_tracks_url, headers)
    top_artists_data = make_spotify_request(top_artists_url, headers)

    top_tracks = [
        {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'preview_url': track.get('preview_url')
        }
        for track in top_tracks_data.get('items', [])
    ] if top_tracks_data else []

    top_artists = [
        {
            'name': artist['name'],
            'image': artist['images'][0]['url'] if artist['images'] else None,
        }
        for artist in top_artists_data.get('items', [])
    ] if top_artists_data else []

    return top_tracks, top_artists


def get_total_listening_time(access_token, time_range='long_term'):
    """
    Estimate total listening time using Spotify's recently played and top tracks endpoints
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    recently_played_url = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'
    top_tracks_url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=50'

    recently_played_data = make_spotify_request(recently_played_url, headers)
    top_tracks_data = make_spotify_request(top_tracks_url, headers)

    total_time = 0

    if recently_played_data:
        total_time += sum(track['track']['duration_ms'] for track in recently_played_data.get('items', [])) / 60000

    if top_tracks_data:
        total_time += sum(track['duration_ms'] for track in top_tracks_data.get('items', [])) / 60000

    return total_time


def get_sound_town(access_token, time_range='long_term'):
    """
    Determine Sound Town based on listening habits and artist genres
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    sound_towns = {
        'Nashville, USA': ['country', 'blues', 'rock', 'americana'],
        'Austin, USA': ['country', 'rock', 'indie', 'psychedelic'],
        'New Orleans, USA': ['jazz', 'blues', 'r&b', 'funk'],
        'Detroit, USA': ['motown', 'techno', 'punk', 'hip hop'],
        'Chicago, USA': ['blues', 'house', 'jazz', 'soul'],
        'Los Angeles, USA': ['hip hop', 'rock', 'electronic', 'pop'],
        'Seattle, USA': ['grunge', 'alternative', 'indie rock'],
        'Rio de Janeiro, Brazil': ['samba', 'bossa nova', 'mpb', 'funk'],
        'Buenos Aires, Argentina': ['tango', 'rock', 'electronic', 'folk'],
        'Berlin, Germany': ['techno', 'electronic', 'industrial', 'experimental'],
        'London, UK': ['punk', 'rock', 'grime', 'electronic', 'indie'],
        'Tokyo, Japan': ['j-pop', 'rock', 'electronic', 'city pop'],
        'Seoul, South Korea': ['k-pop', 'hip hop', 'rock', 'electronic'],
        'New York City, USA': ['hip hop', 'jazz', 'punk', 'salsa']
    }

    artists_url = f"https://api.spotify.com/v1/me/top/artists?limit=50&time_range={time_range}"
    artists_data = make_spotify_request(artists_url, headers)

    if not artists_data:
        return 'Unknown'

    all_artist_genres = [genre.lower() for artist in artists_data.get('items', []) for genre in artist['genres']]

    if not all_artist_genres:
        return 'Unknown'

    potential_towns = [
        (town, sum(1 for genre in all_artist_genres if genre in [t.lower() for t in town_genres]))
        for town, town_genres in sound_towns.items()
    ]
    
    return max(potential_towns, key=lambda x: x[1])[0] if potential_towns else 'Unknown'


def get_listening_character(access_token, time_range='long_term'):
    """
    Determine listening character based on top genres
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}"
    artists_data = make_spotify_request(url, headers)

    if not artists_data:
        return 'Unknown'

    genres = [genre for artist in artists_data.get('items', []) for genre in artist['genres']]

    if 'rock' in genres:
        return 'Rock Rebel'
    elif 'pop' in genres:
        return 'Pop Enthusiast'
    elif 'hip hop' in genres:
        return 'Hip Hop Maverick'
    else:
        return 'Eclectic Explorer'


def get_top_genres(access_token, time_range='long_term'):
    """
    Get top 5 genres based on top artists
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/top/artists?limit=50&time_range={time_range}"
    artists_data = make_spotify_request(url, headers)

    if not artists_data:
        return []

    genre_count = {}
    for artist in artists_data.get('items', []):
        for genre in artist['genres']:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    return [genre for genre, _ in sorted_genres[:5]]


def get_top_artists(access_token, time_range='long_term'):
    """
    Fetch the user's top artists based on the selected time range.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/top/artists?limit=5&time_range={time_range}"
    artists_data = make_spotify_request(url, headers)

    if not artists_data:
        return []

    return [
        {
            'name': artist['name'],
            'image': artist['images'][0]['url'] if artist['images'] else None,
        }
        for artist in artists_data.get('items', [])
    ]


def get_top_tracks(access_token, time_range='long_term'):
    """
    Fetch the user's top tracks based on the selected time range.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/top/tracks?limit=5&time_range={time_range}"
    tracks_data = make_spotify_request(url, headers)

    if not tracks_data:
        return []

    return [
        {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'preview_url': track.get('preview_url')
        }
        for track in tracks_data.get('items', [])
    ]


def generate_genre_persona(access_token, time_range='long_term'):
    return "To test LLM API, comment first line in generate_genre_persona from spotify_util.py"

    # First, get the info
    top_genres = get_top_genres(access_token, time_range)
    top_songs = get_top_tracks(access_token, time_range)
    top_artists = get_top_artists(access_token, time_range)

    if not top_genres:
        return "A music lover with a unique taste that defies easy categorization."

    # Construct a prompt based on top genres
    prompt = f"""
    I listen to music primarily in these genres: {', '.join(top_genres)}. 
    Specifically, I listen to these songs: {', '.join([song['name'] for song in top_songs])}; 
    and these artists: {', '.join([artist['name'] for artist in top_artists])}. 
    How do you think I would dress, think, and act? Keep your response to less than 100 words.
    """

    try:
        client = anthropic.Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY')
        )
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=256,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error generating persona: {e}")
        return "A music lover with an eclectic and unpredictable spirit."
