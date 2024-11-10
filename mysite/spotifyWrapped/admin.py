from django.contrib import admin
from .models import SpotifyTrack

@admin.register(SpotifyTrack)
class SpotifyTrackAdmin(admin.ModelAdmin):
    list_display = ('track_name', 'artist_name', 'period', 'created_at')
    search_fields = ('track_name', 'artist_name')
    list_filter = ('period', 'created_at')