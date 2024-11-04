from django.urls import path
from django.urls import path
from . import views

from . import views
from .views import SpotifyLoginView, SpotifyCallbackView

app_name = "spotifyWrapped"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('home/', views.HomeView.as_view(), name='home'),
]