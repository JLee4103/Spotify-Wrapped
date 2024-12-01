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
from .models import CommunitySlideshow, SpotifyTrack, Score
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .spotify_util import (
    get_total_listening_time,
    get_sound_town,
    get_listening_character,
    get_top_genres,
    get_top_artists,
    get_top_tracks,
    generate_genre_persona,
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
            return redirect('spotifyWrapped:initial_login')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, 'This account has been deactivated.')
            return self.form_invalid(form)
        return super().form_valid(form)

def custom_login(request):
    return CustomLoginView.as_view()(request)


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
        request.session.flush()  # Clear previous session entirely
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
            "client_id": SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "scope": scope,
            "show_dialog": "true",  # Always prompt for Spotify re-login
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

        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                tokens = response.json()
                # Store tokens in session
                request.session["access_token"] = tokens.get("access_token")
                request.session["refresh_token"] = tokens.get("refresh_token")
                
                # Get user profile
                profile_data = make_spotify_api_call(request, "me")
                if profile_data:
                    request.session["spotify_username"] = profile_data.get("display_name")
                    
                    # Update or create user
                    user = request.user
                    if user.is_authenticated:
                        user.spotify_id = profile_data["id"]
                        user.save()
                    
                    return redirect("spotifyWrapped:home")
            
            # If token request failed
            return redirect("spotifyWrapped:spotify_login")
            
        except Exception as e:
            print(f"Error in callback: {str(e)}")
            return redirect("spotifyWrapped:spotify_login")



class HomeView(View):
    template_name = "spotifyWrapped/home.html"
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("spotifyWrapped:login")
            
        access_token = request.session.get("access_token")
        if not access_token:
            return redirect("spotifyWrapped:spotify_login")
            
        username = request.session.get("spotify_username", "Guest")
        wraps = Slideshow.objects.filter(user=request.user).order_by('-date_generated')
        
        return render(request, self.template_name, {
            "username": username,
            "wraps": wraps,
            "wrap_count": wraps.count(),
        })


class SlideshowView(View):
    template_name = "spotifyWrapped/slideshow.html"

    def get(self, request):
        user_id = request.GET.get("user_id")
        slideshow_id = request.GET.get("slideshow_id")

        # If viewing from community page, load the saved slideshow
        if user_id and slideshow_id:
            try:
                community_slideshow = CommunitySlideshow.objects.get(
                    original_slideshow_id=slideshow_id,
                    shared_by_id=user_id
                )
                
                # Get the original slideshow data
                slideshow = community_slideshow.original_slideshow
                
                return render(request, self.template_name, {
                    "slideshow_data": {
                        "intro": f"{slideshow.title}",
                        "total_listening_time": slideshow.total_listening_time,
                        "sound_town": slideshow.sound_town,
                        "listening_character": slideshow.listening_character,
                        "top_genres": slideshow.top_genres,
                        "top_artists": slideshow.top_artists,
                        "top_tracks": slideshow.top_tracks,
                        "genre_persona": slideshow.genre_persona
                    },
                    "period": slideshow.period
                })
            except CommunitySlideshow.DoesNotExist:
                return redirect("spotifyWrapped:community")

        # If viewing personal slideshow, continue with existing code
        period = request.GET.get("period", "Past Year")
        # ... rest of your existing code for personal slideshow ...


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

            # Extract the album image of the first track for the cover
            album_image = tracks[0].get("album_image") if tracks else None

            slideshow = Slideshow.objects.create(
                user=request.user,
                title=f"Spotify Wrapped - {period}",
                period=period,
                top_tracks=album_image,  # Save the album image URL
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

            print(f"Attempting to delete slideshow ID: {slideshow_id} for user: {request.user}")
            slideshow = Slideshow.objects.get(id=slideshow_id, user=request.user)
            slideshow.delete()
            print(f"Slideshow ID: {slideshow_id} deleted successfully.")

            return JsonResponse({
                "success": True,
                "message": "Slideshow deleted successfully"
            })
        except Slideshow.DoesNotExist:
            print(f"Slideshow ID: {slideshow_id} not found for user: {request.user}")
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


from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
import requests

def logout_view(request):
    # Step 1: Revoke Spotify access token (invalidate on Spotify's server)
    access_token = request.session.get("access_token")
    if access_token:
        try:
            revoke_url = "https://accounts.spotify.com/api/token"
            data = {
                "token": access_token,
                "client_id": SPOTIFY_CLIENT_ID,
                "client_secret": SPOTIFY_CLIENT_SECRET,
            }
            requests.post(revoke_url, data=data)
        except Exception as e:
            print(f"Error revoking Spotify token: {e}")

    # Step 2: Clear all session data (including Spotify-specific keys)
    request.session.flush()

    # Step 3: Log the user out of Django
    logout(request)

    # Step 4: Redirect to the login page (ensure user must reauthenticate)
    return redirect(reverse("spotifyWrapped:login"))


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

from django.views.generic import TemplateView

class DevTeamView(TemplateView):
    template_name = 'spotifyWrapped/devteam.html'

from django.http import JsonResponse
from django.views import View
from django.shortcuts import render


class ShareSlideshowView(View):
    def post(self, request, slideshow_id):
        try:
            slideshow = Slideshow.objects.get(id=slideshow_id)
            CommunitySlideshow.objects.create(
                original_slideshow=slideshow,
                shared_by=request.user
            )
            return JsonResponse({
                "success": True,
                "message": "Slideshow shared to community"
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)
            
class CommunityView(View):
    template_name = "spotifyWrapped/community.html"
    
    def get(self, request):
        # Fetch ALL shared slideshows, not just the current user's
        shared_slideshows = CommunitySlideshow.objects.all().order_by('-shared_date')
        
        return render(request, self.template_name, {
            "shared_slideshows": shared_slideshows,
            "username": request.session.get("spotify_username", "Guest")
        })
        
        
        
@login_required
def deactivate_account(request):
    if request.method == 'POST':
        user = request.user
        # First clear all Spotify session data
        request.session.pop('access_token', None)
        request.session.pop('refresh_token', None)
        request.session.pop('spotify_username', None)
        # Then deactivate the user
        user.is_active = False
        user.save()
        # Finally logout
        logout(request)
        messages.success(request, 'Your account has been deactivated successfully.')
        return redirect('spotifyWrapped:login')
    return render(request, 'spotifyWrapped/deactivate.html')