from django.urls import path

from . import views

app_name = "wrapped"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("spotify-test/", views.spotify_test, name="spotify_test"),
]