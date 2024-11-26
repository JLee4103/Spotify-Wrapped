# Generated by Django 5.1 on 2024-11-26 20:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Score",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("player_name", models.CharField(max_length=100)),
                ("score", models.IntegerField()),
                ("date", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="SpotifyTrack",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("track_name", models.CharField(max_length=200)),
                ("artist_name", models.CharField(max_length=200)),
                ("album_name", models.CharField(max_length=200)),
                ("image_url", models.URLField(blank=True, max_length=500, null=True)),
                ("spotify_url", models.URLField(max_length=500)),
                ("preview_url", models.URLField(blank=True, max_length=500, null=True)),
                ("popularity", models.IntegerField(default=0)),
                ("period", models.CharField(max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
