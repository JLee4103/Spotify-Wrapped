from django.shortcuts import render, redirect
from django.views import View
import requests
from .spotify_util import get_spotify_wrapped_data
import spotifyWrapped.settings
from django.contrib.auth import logout

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

        # Only fetch data if user is authenticated with Spotify
        if access_token:
            top_tracks, top_artists = get_spotify_wrapped_data(access_token)
            followers = self.get_spotify_following(access_token)

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

class SlideshowView(View):
    template_name = 'spotifyWrapped/slideshow.html'

    def get(self, request):
        period = request.GET.get('period', 'Past Year')
        access_token = request.session.get('access_token')

        top_tracks = []

        if access_token:
            # Fetch top tracks using the helper function
            top_tracks, _ = get_spotify_wrapped_data(
                access_token,
                period,
                refresh_access_token_callback=self.refresh_access_token_callback
            )

        return render(request, self.template_name, {
            "top_tracks": top_tracks,
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


class SearchFriendView(View):
    template_name = 'spotifyWrapped/search_friend.html'

    def get(self, request):
        # Render search page for the friend
        return render(request, self.template_name)

    def post(self, request):
        # Get the friend's username or public ID from the form
        friend_username = request.POST.get("friend_username")
        
        if friend_username:
            # Redirect to view the friend's wrapped
            return redirect("spotifyWrapped:view_friend_wrapped", friend_username=friend_username)

        return render(request, self.template_name, {'error': 'Please enter a valid Spotify username.'})


class FriendWrappedView(View):
    template_name = 'spotifyWrapped/friend_wrapped.html'

    def get(self, request):
        friend_username = request.GET.get('friend_username')

        # Fetch friend's data based on username (this could be another API call)
        # You may need to query your database or fetch friend-specific data here

        # For example, fetching top tracks/artists for the friend
        access_token = request.session.get('access_token')
        if access_token and friend_username:
            top_tracks, top_artists = get_spotify_wrapped_data(access_token)
        else:
            top_tracks, top_artists = [], []

        return render(request, self.template_name, {
            'friend_username': friend_username,
            'top_tracks': top_tracks,
            'top_artists': top_artists,
        })
    

def logout_view(request):
    logout(request)
    return redirect('spotifyWrapped:initial_login')

