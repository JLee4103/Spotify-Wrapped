from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import DeleteSlideshowView, SpotifyLoginView, SpotifyCallbackView, SlideshowView, logout_view, SpotifyInitialLogin

app_name = "spotifyWrapped"

urlpatterns = [
    # Root URL redirects to login page
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # login path

    # Registration paths
    path('register/', views.register, name='register'),

    # Spotify-related URLs
    path('spotify/login/', SpotifyLoginView.as_view(), name='spotify_login'),  # Renamed to avoid conflict
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),

    # Initial login page
    path('initial_login/', SpotifyInitialLogin.as_view(), name='initial_login'),

    # Other application paths
    path('home/', views.HomeView.as_view(), name='home'),
    path('slideshow/', SlideshowView.as_view(), name='slideshow'),
    path('save-slideshow/', views.SaveSlideshowView.as_view(), name='save_slideshow'),
    path('delete-slideshow/<int:slideshow_id>/', DeleteSlideshowView.as_view(), name='delete_slideshow'),
    path('logout/', logout_view, name='logout'),

    path('community/', views.CommunityView.as_view(), name='community'),
    path('share-to-community/<int:slideshow_id>/', views.ShareSlideshowView.as_view(), name='share_to_community'),
    
    # Game-related URLs
    path('game/', views.GameView.as_view(), name='game'),
    path('save_score/', views.save_score, name='save_score'),
    path('high_scores/', views.high_scores, name='high_scores'),

    path('dev-team/', views.DevTeamView.as_view(), name='dev_team'),

]
