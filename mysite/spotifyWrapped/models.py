from django.db import models

class SpotifyTrack(models.Model):
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
