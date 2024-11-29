from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from django.utils import timezone
import random
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from django.db import transaction
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



from urllib.parse import urlencode

class SpotifyLoginView(View):
    def get(self, request):
        request.session.flush()
        spotify_auth_url = "https://accounts.spotify.com/authorize"
        scope = (
            "user-top-read "
            "user-follow-read "
            "user-library-read "
            "user-read-private "
            "playlist-read-private "
            "user-read-recently-played "
            "user-read-playback-state "
            "user-modify-playback-state"
        )
        query_params = {
            'client_id': SPOTIFY_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'scope': scope
        }
        auth_url = f"{spotify_auth_url}?{urlencode(query_params)}"
        return redirect(auth_url)


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
        if not request.user.is_authenticated:
            return redirect("spotifyWrapped:spotify_login")

        username = request.session.get("spotify_username", "Guest")
        
        # Get all slideshows for the user
        wraps = Slideshow.objects.filter(user=request.user).order_by('-date_generated')

        return render(request, self.template_name, {
            "username": username,
            "wraps": wraps,
            "wrap_count": wraps.count(),
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
        except Exception as e:
            print(f"Error fetching slideshow data: {e}")

        # Serialize the top_tracks data
        slideshow_data['top_tracks_json'] = json.dumps(slideshow_data['top_tracks'], cls=DjangoJSONEncoder)

        return render(
            request, 
            self.template_name, 
            {
                "slideshow_data": slideshow_data, 
                "period": period
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class SaveSlideshowView(View):
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    "success": False, 
                    "error": "User not authenticated"
                }, status=401)

            data = json.loads(request.body)
            period = data.get("period", "Unknown Period")
            tracks = data.get("tracks", [])

            if not tracks:
                return JsonResponse({
                    "success": False,
                    "error": "No tracks provided"
                }, status=400)

            # Create a single slideshow entry
            slideshow = Slideshow.objects.create(
                user=request.user,
                title=f"Spotify Wrapped - {period}",
                period=period,
                top_tracks=tracks,  # This will be saved in the JSONField
                date_generated=timezone.now()
            )

            return JsonResponse({
                "success": True,
                "message": "Slideshow saved successfully",
                "slideshow_id": slideshow.id
            })

        except Exception as e:
            print(f"Error saving slideshow: {str(e)}")
            return JsonResponse({
                "success": False,
                "error": "An error occurred while saving the slideshow"
            }, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class DeleteSlideshowView(View):
    def post(self, request, slideshow_id):
        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    "success": False, 
                    "error": "User not authenticated"
                }, status=401)

            # Delete the specific slideshow
            slideshow = Slideshow.objects.get(id=slideshow_id, user=request.user)
            slideshow.delete()

            return JsonResponse({
                "success": True,
                "message": "Slideshow deleted successfully"
            })
        except Slideshow.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Slideshow not found"
            }, status=404)
        except Exception as e:
            print(f"Error in DeleteSlideshowView: {str(e)}")
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)


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
