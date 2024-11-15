from django.shortcuts import render, redirect
from django.views import View
import requests
import spotifyWrapped.settings
from django.contrib.auth import logout
from .models import SpotifyTrack
from django.db.models import Max
from django.db.models.functions import TruncDay
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .spotify_util import (
    get_total_listening_time,
    get_sound_town,
    get_listening_character,
    get_top_genres,
    get_top_artists,
    get_top_tracks,
    get_spotify_wrapped_data
)

class SpotifyInitialLogin(View):
    def get(self, request):
        if request.session.get("spotify_username"):
            return redirect("spotifyWrapped:home")
        return render(request, "spotifyWrapped/initialLogin.html")

    
class SpotifyLoginView(View):
    def get(self, request):
        # Clear previous tokens
        request.session.flush()  # This clears all session data, including tokens
        
        spotify_auth_url = 'https://accounts.spotify.com/authorize'
        response_type = 'code'
        scope = 'user-top-read user-follow-read'  # Ensure both 'user-top-read' and 'user-follow-read' are included

        # Construct the Spotify authorization URL
        auth_url = (
            f"{spotify_auth_url}?client_id={spotifyWrapped.settings.SPOTIFY_CLIENT_ID}"
            f"&response_type={response_type}"
            f"&redirect_uri={spotifyWrapped.settings.SPOTIFY_REDIRECT_URI}"
            f"&scope={scope}"
        )

        # Redirect the user to the Spotify authorization page
        return redirect(auth_url)



class SpotifyCallbackView(View):
    def get(self, request):
        auth_code = request.GET.get("code")
        url = "https://accounts.spotify.com/api/token"

        # Headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Data payload
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": spotifyWrapped.settings.SPOTIFY_REDIRECT_URI,
            "client_id": spotifyWrapped.settings.SPOTIFY_CLIENT_ID,
            "client_secret": spotifyWrapped.settings.SPOTIFY_CLIENT_SECRET,
        }

        # Make the POST request to exchange the code for tokens
        response = requests.post(url, data=data)

        # Check if the request was successful and handle tokens
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")

            # Save tokens to session
            request.session['access_token'] = access_token
            if refresh_token:
                request.session['refresh_token'] = refresh_token

            # Fetch user data
            profile_url = "https://api.spotify.com/v1/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(profile_url, headers=headers)
            profile_data = profile_response.json()

            # Save username to session
            request.session['spotify_username'] = profile_data.get("display_name")

        # Redirect to the home page after successful authentication
        return redirect("spotifyWrapped:home")


class HomeView(View):
    template_name = 'spotifyWrapped/home.html'

    def get(self, request):
        username = request.session.get("spotify_username", "Guest")
        access_token = request.session.get('access_token')
        followers = []
        top_tracks, top_artists = [], []

        # Get saved wraps from database
        saved_wraps = self.get_saved_wraps()

        # Only fetch data if user is authenticated with Spotify
        if access_token:
            try:
                # Use the individual getter functions instead of get_spotify_wrapped_data
                top_tracks = get_top_tracks(access_token)
                top_artists = get_top_artists(access_token)
                followers = self.get_spotify_following(access_token)
            except Exception as e:
                print(f"Error fetching Spotify data: {e}")

        return render(request, self.template_name, {
            "username": username,
            "top_tracks": top_tracks,
            "top_artists": top_artists,
            "followers": followers,
        })

    def get_spotify_following(self, access_token):
        following_url = "https://api.spotify.com/v1/me/following?type=user&limit=50"
        headers = {"Authorization": f"Bearer {access_token}"}

        following = []
        while following_url:
            response = requests.get(following_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                following.extend(data['artists'])  # 'artists' because 'following' is type 'user' or 'artist'
                following_url = data.get('next')  # Pagination to get more followings
            else:
                print("Failed to fetch following:", response.json())
                break

        return [{'username': user['name']} for user in following]
    
        
    def get_saved_wraps(self):
        try:
            # Group tracks by period and created_at
            from django.db.models import Max
            from django.db.models.functions import TruncDay

            wraps = SpotifyTrack.objects.annotate(
                date=TruncDay('created_at')
            ).values('date', 'period').annotate(
                latest=Max('created_at')
            ).order_by('-date')

            formatted_wraps = []
            for wrap in wraps:
                tracks = SpotifyTrack.objects.filter(
                    created_at__date=wrap['date'],
                    period=wrap['period']
                ).order_by('-popularity')

                formatted_wraps.append({
                    'title': f"Spotify Wrapped - {wrap['period']}",
                    'date_generated': wrap['date'],
                    'tracks': [{
                        'name': track.track_name,
                        'artist': track.artist_name,
                        'album_image': track.image_url,
                        'preview_url': None,
                    } for track in tracks]
                })

            return formatted_wraps
        except Exception as e:
            print(f"Error getting saved wraps: {str(e)}")
            return []

class SlideshowView(View):
    template_name = 'spotifyWrapped/slideshow.html'

    def get(self, request):
        period = request.GET.get('period', 'Past Year')
        access_token = request.session.get('access_token')

        # Map user-selected period to Spotify API time ranges
        time_range_map = {
            'Past Month': 'short_term',
            'Past 6 Months': 'medium_term',
            'Past Year': 'long_term'
        }
        selected_time_range = time_range_map.get(period, 'long_term')

        # Initialize slides with default/placeholder data
        slideshow_data = {
            'intro': f"Here's your Spotify Wrapped for {period}!",
            'total_listening_time': 0,
            'sound_town': "Unknown",
            'listening_character': "Unknown",
            'top_genres': [],
            'top_artists': [],
            'top_tracks': []
        }

        if access_token:
            try:
                # Pass the selected time range to all functions
                slideshow_data['total_listening_time'] = get_total_listening_time(
                    access_token,
                    time_range=selected_time_range
                )
                slideshow_data['sound_town'] = get_sound_town(
                    access_token,
                    time_range=selected_time_range
                )
                slideshow_data['listening_character'] = get_listening_character(
                    access_token,
                    time_range=selected_time_range
                )
                slideshow_data['top_genres'] = get_top_genres(
                    access_token,
                    time_range=selected_time_range
                )
                slideshow_data['top_artists'] = get_top_artists(
                    access_token,
                    time_range=selected_time_range
                )
                slideshow_data['top_tracks'] = get_top_tracks(
                    access_token,
                    time_range=selected_time_range
                )

            except Exception as e:
                # Log the error and keep default values
                print(f"Error fetching Spotify data: {e}")

        return render(request, self.template_name, {
            "slideshow_data": slideshow_data,
            "period": period
        })

    def refresh_access_token_callback(self):
        refresh_token = self.request.session.get('refresh_token')
        if refresh_token:
            return self.refresh_access_token(refresh_token)
        return None

    def refresh_access_token(self, refresh_token):
        url = "https://accounts.spotify.com/api/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": spotifyWrapped.settings.SPOTIFY_CLIENT_ID,
            "client_secret": spotifyWrapped.settings.SPOTIFY_CLIENT_SECRET,
        }
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            tokens = response.json()
            new_access_token = tokens.get("access_token")
            self.request.session['access_token'] = new_access_token
            return new_access_token
        else:
            print("Failed to refresh access token:", response.json())
            return None
        
@method_decorator(csrf_exempt, name='dispatch')
class SaveSlideshowView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            tracks = data.get('tracks', [])
            period = data.get('period', 'Unknown Period')
           # username = request.session.get('spotify_username', 'Unknown User')

            # Delete existing tracks for this period and user before saving new ones
            SpotifyTrack.objects.filter(
              #  username=username,
                period=period
            ).delete()

            # Save new tracks
            for track in tracks:
                SpotifyTrack.objects.create(
                  #  username=username,
                    track_name=track.get('name', ''),
                    artist_name=track.get('artists', [{}])[0].get('name', ''),
                    album_name=track.get('album', {}).get('name', ''),
                    image_url=track.get('album', {}).get('images', [{}])[0].get('url', ''),
                    spotify_url=track.get('external_urls', {}).get('spotify', ''),
                    preview_url=track.get('preview_url'),
                    popularity=track.get('popularity', 0),
                    period=period
                )

            return JsonResponse({
                'success': True,
                'message': 'Slideshow saved successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
            
@method_decorator(csrf_exempt, name='dispatch')
class DeleteSlideshowView(View):
    def post(self, request):
        try:
            # Get username from session
           # username = request.session.get('spotify_username')
            # Parse JSON data from request body
            data = json.loads(request.body)

           # print(f"Delete attempt - Username: {username}, Period: {period}")  # Debug logging



            # Delete all tracks for this specific period and user
            deleted_count = SpotifyTrack.objects.filter(
              #  username=username,
            ).delete()
            
            print(f"Deleted {deleted_count[0]} tracks")  # Debug logging
            
            return JsonResponse({
                'success': True,
                'message': f'Deleted {deleted_count[0]} tracks'
            })
                
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


def logout_view(request):
    logout(request)
    return redirect('spotifyWrapped:initial_login')

from django.shortcuts import render
from django.http import JsonResponse
from .models import Score
import random

class GameView(View):
    template_name = 'spotifyWrapped/game.html'

    def get(self, request):
        # Fetch a random song for the game
        access_token = request.session.get('access_token')
        song = get_random_song(access_token)

        if song:
            # If we have a song, pass it to the template
            return render(request, self.template_name, {
                'song_name': song.get('name', 'Unknown'),
                'song_artist': song.get('artist', 'Unknown'),
                'song_bpm': song.get('bpm', 120),  # Default BPM if not found
                'preview_url': song.get('preview_url', ''),
            })
        else:
            # Fallback if no song was found
            return render(request, self.template_name, {
                'error_message': 'No song found to play in the game.'
            })

def save_score(request):
    if request.method == "POST":
        player_name = request.POST.get('player_name')
        score = int(request.POST.get('score'))
        Score.objects.create(player_name=player_name, score=score)
        return JsonResponse({'status': 'success'})

def high_scores(request):
    scores = Score.objects.all().order_by('-score')[:10]
    data = [{'player_name': s.player_name, 'score': s.score} for s in scores]
    return JsonResponse({'high_scores': data})

# Function to fetch BPM (Tempo) for a song from Spotify's API
def get_bpm(track_id, access_token):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('tempo', None)  # 'tempo' contains the BPM
    else:
        print(f"Failed to get BPM for track {track_id}")
        return None

# Get a random song and its BPM
def get_random_song(access_token, period='Past Year'):
    top_tracks, _ = get_spotify_wrapped_data(access_token, period)
    
    # Randomly pick a song from the top tracks list
    if top_tracks:
        random_song = random.choice(top_tracks)
        track_id = random_song.get('id')  # Get the track's ID
        bpm = get_bpm(track_id, access_token)
        
        # Return the song and its BPM
        if bpm:
            random_song['bpm'] = bpm  # Add BPM to the song data
            return random_song
        else:
            print("BPM not available for this track.")
            return None
    return None

@method_decorator(csrf_exempt, name='dispatch')
class SaveScoreView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            player_name = data.get('player_name')
            score = int(data.get('score'))

            # Save the score to the database
            Score.objects.create(player_name=player_name, score=score)
            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)