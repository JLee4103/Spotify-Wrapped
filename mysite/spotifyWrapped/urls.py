from django.urls import path
from . import views
from .views import SpotifyLoginView, SpotifyCallbackView, SlideshowView, logout_view, SpotifyInitialLogin

app_name = "spotifyWrapped"
urlpatterns = [
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('login/', SpotifyLoginView.as_view(), name='spotify_login'),
    path('slideshow', SlideshowView.as_view(), name='slideshow'),
    path('logout/', logout_view, name='logout'),
    path("", views.SpotifyInitialLogin.as_view(), name = "initial_login"),
]