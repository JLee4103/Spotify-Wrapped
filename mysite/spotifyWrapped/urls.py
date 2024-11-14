from django.urls import path
from . import views
from .views import SpotifyLoginView, SpotifyCallbackView, SlideshowView, logout_view, SpotifyInitialLogin

app_name = "spotifyWrapped"

urlpatterns = [
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('login/', SpotifyLoginView.as_view(), name='spotify_login'),
    path('slideshow', SlideshowView.as_view(), name='slideshow'),
    path('save-slideshow/', views.SaveSlideshowView.as_view(), name='save_slideshow'),
    path('delete-slideshow/', views.DeleteSlideshowView.as_view(), name='delete_slideshow'),
    path('logout/', logout_view, name='logout'),
    path("", views.SpotifyInitialLogin.as_view(), name = "initial_login"),
    path('game/', views.game_view, name='game'),
    path('save_score/', views.save_score, name='save_score'),
    path('high_scores/', views.high_scores, name='high_scores'),
]
