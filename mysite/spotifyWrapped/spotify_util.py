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

def get_total_listening_time(access_token, time_range='long_term'):
    """
    Estimate total listening time using Spotify's recently played and top tracks endpoints
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    # Use multiple endpoints to get a more comprehensive listening time
    recently_played_url = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'
    top_tracks_url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=50'

    try:
        # Fetch recently played tracks
        recently_played_response = requests.get(recently_played_url, headers=headers)

        # Fetch top tracks
        top_tracks_response = requests.get(top_tracks_url, headers=headers)

        total_time = 0

        # Calculate time from recently played tracks
        if recently_played_response.status_code == 200:
            recently_played_tracks = recently_played_response.json().get('items', [])
            total_time += sum(track['track']['duration_ms'] for track in recently_played_tracks) / 60000

        # Calculate time from top tracks
        if top_tracks_response.status_code == 200:
            top_tracks = top_tracks_response.json().get('items', [])
            total_time += sum(track['duration_ms'] for track in top_tracks) / 60000

        return total_time

    except Exception as e:
        print(f"Error fetching listening time: {e}")
        return 0

    except Exception as e:
        print(f'Error fetching listening time: {e}')
        return 0


def get_sound_town(access_token, time_range='long_term'):
    """
    Determine Sound Town based on listening habits and artist genres
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    # Comprehensive list of Sound Towns
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

    try:
        # Fetch top artists
        artists_url = f"https://api.spotify.com/v1/me/top/artists?limit=50&time_range={time_range}"
        artists_response = requests.get(artists_url, headers=headers)

        if artists_response.status_code == 200:
            top_artists = artists_response.json()['items']

            # If no top artists found, return Unknown
            if not top_artists:
                return 'Unknown'

            # Collect all genres from top artists
            all_artist_genres = []
            for artist in top_artists:
                # Convert genres to lowercase for better matching
                all_artist_genres.extend([genre.lower() for genre in artist['genres']])

            # If no genres found, return Unknown
            if not all_artist_genres:
                return 'Unknown'

            # Scoring for town matching
            potential_towns = []
            for town, town_genres in sound_towns.items():
                # Convert town genres to lowercase
                town_genres = [genre.lower() for genre in town_genres]

                # Count genre matches
                genre_matches = sum(1 for genre in all_artist_genres if genre in town_genres)

                if genre_matches > 0:
                    potential_towns.append((town, genre_matches))

            # Return the town with the most genre matches
            if potential_towns:
                return max(potential_towns, key=lambda x: x[1])[0]

    except Exception as e:
        print(f"Error fetching sound town: {e}")

    return 'Unknown'


def get_listening_character(access_token, time_range='long_term'):
    """
    Determine listening character based on top genres
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            artists = response.json()['items']
            genres = [genre for artist in artists for genre in artist['genres']]

            if 'rock' in genres:
                return 'Rock Rebel'
            elif 'pop' in genres:
                return 'Pop Enthusiast'
            elif 'hip hop' in genres:
                return 'Hip Hop Maverick'
            else:
                return 'Eclectic Explorer'
    except Exception as e:
        print(f"Error fetching listening character: {e}")
    return 'Unknown'


def get_top_genres(access_token, time_range='long_term'):
    """
    Get top 5 genres based on top artists
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/top/artists?limit=50&time_range={time_range}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            artists = response.json()['items']
            genre_count = {}
            for artist in artists:
                for genre in artist['genres']:
                    genre_count[genre] = genre_count.get(genre, 0) + 1

            sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
            return [genre for genre, count in sorted_genres[:5]]
    except Exception as e:
        print(f"Error fetching top genres: {e}")
    return []



def get_top_artists(access_token, time_range='long_term'):
    """
    Fetch the user's top artists from Spotify based on the selected time range.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            artists = response.json()['items']
            return [
                {
                    'name': artist['name'],
                    'image': artist['images'][0]['url'] if artist['images'] else None,
                }
                for artist in artists
            ]
    except Exception as e:
        print(f"Error fetching top artists: {e}")
    return []  # Return an empty list if there's an error.



def get_top_tracks(access_token, time_range='long_term'):
    """
    Fetch the user's top tracks from Spotify based on the selected time range.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={time_range}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tracks = response.json()['items']
            return [
                {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track.get('preview_url')
                }
                for track in tracks
            ]
    except Exception as e:
        print(f"Error fetching top tracks: {e}")
    return []  # Return an empty list if there's an error.