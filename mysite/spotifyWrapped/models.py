from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class SpotifyTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track_name = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    album_name = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    spotify_url = models.URLField(max_length=500)
    preview_url = models.URLField(max_length=500, null=True, blank=True)  # Add this field
    popularity = models.IntegerField(default=0)
    period = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.track_name} - {self.artist_name}"
    
    from django.db import models

class Score(models.Model):
    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    
class Slideshow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date_generated = models.DateTimeField(auto_now_add=True)
    total_listening_time = models.IntegerField(default=0)
    sound_town = models.CharField(max_length=255, default="Unknown")
    listening_character = models.CharField(max_length=255, default="Unknown")
    top_genres = models.JSONField(default=list)
    top_artists = models.JSONField(default=list)
    top_tracks = models.JSONField(default=list)
    genre_persona = models.TextField(null=True, blank=True)
    period = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.title} - {self.user.username}"