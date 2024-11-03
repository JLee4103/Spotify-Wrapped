import requests
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.conf import settings  # Use settings for Spotify credentials
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import F
from .models import Choice, Question
import spotifyWrapped.settings


class SpotifyLoginView(View):
    def get(self, request):
        spotify_auth_url = 'https://accounts.spotify.com/authorize'
        response_type = 'code'
        scope = 'user-top-read'

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

        # Make the POST request
        response = requests.post(url, data=data)

        # Check if the request was successful and print the token
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")  # Only if using auth code flow

            # Save tokens to session
            request.session['access_token'] = access_token
            if refresh_token:
                request.session['refresh_token'] = refresh_token

            # fetch user data
            profile_url = "https://api.spotify.com/v1/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(profile_url, headers=headers)
            profile_data = profile_response.json()

            #save username to session
            request.session['spotify_username'] = profile_data.get("display_name")
            #Uncomment next line for debugging
            #print(profile_data)
        # Redirect to the top songs view or home page after successful authentication
        return redirect("spotifyWrapped:home")


class HomeView(View):
    template_name = 'spotifyWrapped/home.html'

    def get(self, request):
        username = request.session.get("spotify_username", "Guest")
        
        # Fetch top tracks/artists only if user is authenticated with Spotify
        access_token = request.session.get('access_token', None)
        
        # You may want to get the period from request or session (for example purposes)
        period = request.GET.get('period', 'Past Year')  # Default to "Past Year" if not provided
        
        if access_token:
            # Pass the period argument here
            top_tracks, top_artists = self.get_spotify_wrapped_data(access_token, period)
        else:
            top_tracks, top_artists = [], []

        return render(request, self.template_name, {
            "username": username,
            "top_tracks": top_tracks,
            "top_artists": top_artists,
        })

    def get_spotify_wrapped_data(self, access_token, period):
        """
        Fetches user's top tracks and artists from Spotify based on the selected time range.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Map the selected period to Spotify's time range
        time_range_map = {
            'Past Month': 'short_term',
            'Past 6 Months': 'medium_term',
            'Past Year': 'long_term'
        }
        
        # Get the appropriate time range for Spotify API
        time_range = time_range_map.get(period, 'long_term')
        
        # Fetch user's top tracks from Spotify
        top_tracks_url = f"https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={time_range}"
        top_tracks_response = requests.get(top_tracks_url, headers=headers)
        
        if top_tracks_response.status_code == 200:
            top_tracks_data = top_tracks_response.json().get('items', [])
            top_tracks = [
                {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                }
                for track in top_tracks_data
            ]
        else:
            top_tracks = []
        
        # Fetch user's top artists from Spotify
        top_artists_url = f"https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}"
        top_artists_response = requests.get(top_artists_url, headers=headers)
        
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
            top_artists = []
        
        return top_tracks, top_artists

def get_spotify_wrapped_data(self, access_token, period):
    headers = {"Authorization": f"Bearer {access_token}"}

    # Map the selected period to Spotify's time range
    time_range_map = {
        'Past Month': 'short_term',
        'Past 6 Months': 'medium_term',
        'Past Year': 'long_term'
    }
    
    time_range = time_range_map.get(period, 'long_term')
    
    # Fetch user's top tracks
    top_tracks_url = f"https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={time_range}"
    top_tracks_response = requests.get(top_tracks_url, headers=headers)
    
    if top_tracks_response.status_code == 200:
        top_tracks_data = top_tracks_response.json().get('items', [])
        top_tracks = []
        
        for track in top_tracks_data:
            # Fetch additional details such as duration
            track_id = track['id']
            track_details_url = f"https://api.spotify.com/v1/tracks/{track_id}"
            track_details_response = requests.get(track_details_url, headers=headers)
            if track_details_response.status_code == 200:
                track_details = track_details_response.json()
                duration_ms = track_details.get('duration_ms', 0)  # Default to 0 if not available
                
                # Calculate estimated listening time (for example purposes, assume 10 plays)
                estimated_listening_time_minutes = round((duration_ms / 1000 / 60) * 10, 2) if duration_ms > 0 else 0
                
                top_tracks.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],  
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'estimated_listening_time': estimated_listening_time_minutes
                })
    else:
        top_tracks = []

    return top_tracks


class IndexView(View):
    template_name = "spotifyWrapped/initialLogIn.html"
    
    def get(self, request):
        latest_question_list = Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
        
        context = {
            "latest_question_list": latest_question_list,
        }
        
        return render(request, self.template_name, context)


class DetailView(View):
    template_name = "spotifyWrapped/detail.html"
    
    def get(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        
        context = {
            "question": question,
        }
        
        return render(request, self.template_name, context)


class ResultsView(View):
    template_name = "spotifyWrapped/results.html"
    
    def get(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        
        context = {
            "question": question,
        }
        
        return render(request, self.template_name, context)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "spotifyWrapped/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        
    return HttpResponseRedirect(reverse("spotifyWrapped:results", args=(question.id,)))