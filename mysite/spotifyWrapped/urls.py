from django.urls import path
from django.urls import path
from . import views

from . import views
from .views import SpotifyLoginView, SpotifyCallbackView, SlideshowView  

app_name = "spotifyWrapped"
urlpatterns = [
    path("", views.HomeView.as_view(), name="login"),
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('login/', SpotifyLoginView.as_view(), name='spotify_login'),
    path('slideshow', SlideshowView.as_view(), name='slideshow'),
]