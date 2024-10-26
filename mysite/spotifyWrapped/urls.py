from django.urls import path
from django.urls import path
from . import views

from . import views
from .views import SpotifyLoginView, SpotifyCallbackView

app_name = "spotifyWrapped"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('spotify/login/', SpotifyLoginView.as_view(), name='spotify_login'),
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),
]