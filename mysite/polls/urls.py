from django.urls import path
from django.urls import path
from . import views

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('login/', views.IndexView.spotify_login(), name='spotify_login'),
    path('callback/', views.IndexView.spotify_callback(), name='spotify_callback'),
]