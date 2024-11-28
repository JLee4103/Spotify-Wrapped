from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import random
from .models import SpotifyTrack, Score
from .spotify_util import (
    get_total_listening_time,
    get_sound_town,
    get_listening_character,
    get_top_genres,
    get_top_artists,
    get_top_tracks,
    get_spotify_wrapped_data
)
from spotifyWrapped.settings import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI
)
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from .models import Slideshow
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in automatically after registration
            return redirect('spotifyWrapped:initial_login')  # Redirect after registration
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def custom_login(request):
    return auth_views.LoginView.as_view()(request)


# Utility: Refresh Access Token
def refresh_access_token(request):
    refresh_token = request.session.get("refresh_token")
    if not refresh_token:
        return None

    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        request.session["access_token"] = tokens.get("access_token")
        return tokens.get("access_token")
    else:
        print(f"Failed to refresh token: {response.json()}")
        return None


# Utility: Make Spotify API Call
def make_spotify_api_call(request, endpoint):
    access_token = request.session.get("access_token")
    if not access_token:
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"https://api.spotify.com/v1/{endpoint}", headers=headers)

    if response.status_code == 401:  # Access token expired
        new_token = refresh_access_token(request)
        if new_token:
            headers["Authorization"] = f"Bearer {new_token}"
            response = requests.get(f"https://api.spotify.com/v1/{endpoint}", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Spotify API call failed: {response.json()}")
        return None



# Views
class SpotifyInitialLogin(View):
    def get(self, request):
        # Check if Spotify username exists in session
        if request.session.get("spotify_username"):
            return redirect("spotifyWrapped:home")  # Go to home if already connected

        # If not, show the initial login page
        return render(request, "spotifyWrapped/initialLogin.html")



class SpotifyLoginView(View):
    def get(self, request):
        request.session.flush()  # Clear session data
        spotify_auth_url = "https://accounts.spotify.com/authorize"
        scope = "user-top-read user-follow-read"

        auth_url = (
            f"{spotify_auth_url}?client_id={SPOTIFY_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
            f"&scope={scope}"
        )
        return redirect(auth_url)


from django.contrib.auth import get_user_model

class SpotifyCallbackView(View):
    def get(self, request):
        auth_code = request.GET.get("code")
        if not auth_code:
            print("No authorization code received.")
            return redirect("spotifyWrapped:spotify_login")

        url = "https://accounts.spotify.com/api/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            tokens = response.json()
            request.session["access_token"] = tokens.get("access_token")
            request.session["refresh_token"] = tokens.get("refresh_token")

            profile_data = make_spotify_api_call(request, "me")
            if profile_data:
                request.session["spotify_username"] = profile_data.get("display_name")

                # Optionally associate the Spotify account with a Django user
                User = get_user_model()
                user, created = User.objects.get_or_create(username=profile_data["id"])
                if created:
                    user.set_unusable_password()  # Or set a default password if necessary
                    user.save()

                login(request, user)  # Log in the user

        return redirect("spotifyWrapped:home")




class HomeView(View):
    template_name = "spotifyWrapped/home.html"

    def get(self, request):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            print("User is not authenticated. Redirecting to Spotify login.")
            return redirect("spotifyWrapped:spotify_login")

        username = request.session.get("spotify_username", "Guest")
        access_token = request.session.get("access_token")

        if not access_token:
            print("Access token missing. Attempting to refresh...")
            access_token = refresh_access_token(request)

        if not access_token:
            print("Access token could not be refreshed. Redirecting to Spotify login.")
            return redirect("spotifyWrapped:spotify_login")

        # Query only for authenticated users
        wraps = Slideshow.objects.filter(user=request.user)  # Filter slideshows by the authenticated user
        wrap_count = wraps.count()

        # Fetch Spotify data
        top_tracks = make_spotify_api_call(request, "me/top/tracks?limit=10")
        top_artists = make_spotify_api_call(request, "me/top/artists?limit=10")

        return render(request, self.template_name, {
            "username": username,
            "top_tracks": top_tracks.get("items", []) if top_tracks else [],
            "top_artists": top_artists.get("items", []) if top_artists else [],
            "wraps": wraps,
            "wrap_count": wrap_count,
        })




class SlideshowView(View):
    template_name = "spotifyWrapped/slideshow.html"

    def get(self, request):
        period = request.GET.get("period", "Past Year")
        time_range_map = {
            "Past Month": "short_term",
            "Past 6 Months": "medium_term",
            "Past Year": "long_term",
        }
        selected_time_range = time_range_map.get(period, "long_term")
        access_token = request.session.get("access_token")

        if not access_token:
            return redirect("spotifyWrapped:spotify_login")

        slideshow_data = {
            "intro": f"Here's your Spotify Wrapped for {period}!",
            "total_listening_time": 0,
            "sound_town": "Unknown",
            "listening_character": "Unknown",
            "top_genres": [],
            "top_artists": [],
            "top_tracks": [],
        }

        try:
            slideshow_data.update({
                "total_listening_time": get_total_listening_time(access_token, selected_time_range),
                "sound_town": get_sound_town(access_token, selected_time_range),
                "listening_character": get_listening_character(access_token, selected_time_range),
                "top_genres": get_top_genres(access_token, selected_time_range),
                "top_artists": get_top_artists(access_token, selected_time_range),
                "top_tracks": get_top_tracks(access_token, selected_time_range),
            })

            # Save the slideshow data to the database
            slideshow = Slideshow.objects.create(
                user=request.user,
                title=f"Spotify Wrapped - {period}",
                total_listening_time=slideshow_data["total_listening_time"],
                sound_town=slideshow_data["sound_town"],
                listening_character=slideshow_data["listening_character"],
                top_genres=slideshow_data["top_genres"],
                top_artists=slideshow_data["top_artists"],
                top_tracks=slideshow_data["top_tracks"],
                period=period,
            )
        except Exception as e:
            print(f"Error fetching slideshow data: {e}")

        return render(request, self.template_name, {"slideshow_data": slideshow_data, "period": period})

@method_decorator(csrf_exempt, name="dispatch")
class SaveSlideshowView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            period = data.get("period", "Unknown Period")
            tracks = data.get("tracks", [])

            # Ensure the user is logged in
            user = request.user  # This will get the logged-in user from the request

            # Delete previous tracks for the user and period
            SpotifyTrack.objects.filter(user=user, period=period).delete()

            # Save the new tracks
            for track in tracks:
                SpotifyTrack.objects.create(
                    user=user,  # Associate the track with the logged-in user
                    track_name=track.get("name", ""),
                    artist_name=track.get("artists", [{}])[0].get("name", ""),
                    album_name=track.get("album", {}).get("name", ""),
                    image_url=track.get("album", {}).get("images", [{}])[0].get("url", ""),
                    spotify_url=track.get("external_urls", {}).get("spotify", ""),
                    preview_url=track.get("preview_url"),
                    popularity=track.get("popularity", 0),
                    period=period,
                )

            return JsonResponse({"success": True, "message": "Slideshow saved successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)



@method_decorator(csrf_exempt, name="dispatch")
class DeleteSlideshowView(View):
    def post(self, request):
        try:
            deleted_count = SpotifyTrack.objects.all().delete()
            return JsonResponse({"success": True, "message": f"Deleted {deleted_count[0]} tracks"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


class GameView(View):
    template_name = "spotifyWrapped/game.html"

    def get(self, request):
        access_token = request.session.get("access_token")
        if not access_token:
            return redirect("spotifyWrapped:spotify_login")  # Redirect if no access token

        # Render the game.html template if access token is available
        return render(request, self.template_name)


def logout_view(request):
    logout(request)
    return redirect("spotifyWrapped:initial_login")


def save_score(request):
    if request.method == "POST":
        player_name = request.POST.get("player_name")
        score = int(request.POST.get("score"))
        Score.objects.create(player_name=player_name, score=score)
        return JsonResponse({"status": "success"})


def high_scores(request):
    scores = Score.objects.all().order_by("-score")[:10]
    data = [{"player_name": s.player_name, "score": s.score} for s in scores]
    return JsonResponse({"high_scores": data})
