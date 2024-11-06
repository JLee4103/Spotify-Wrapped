import requests
from django.shortcuts import redirect, render
from django.views import View
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

            # Fetch user data
            profile_url = "https://api.spotify.com/v1/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(profile_url, headers=headers)
            profile_data = profile_response.json()

            # Save username to session
            request.session['spotify_username'] = profile_data.get("display_name")
            # Uncomment next line for debugging
            # print(profile_data)
        
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
                    'preview_url': track.get('preview_url')  # Add preview_url here
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


class IndexView(View):
    template_name = "spotifyWrapped/initialLogIn.html"

    def get(self, request):
        return render(request, 'spotifyWrapped/index.html')
