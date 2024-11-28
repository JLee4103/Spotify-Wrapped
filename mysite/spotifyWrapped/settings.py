# settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

# Use database-backed sessions (default)
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Ensure cookies are secure (especially in production)
SESSION_COOKIE_SECURE = False  # Set True if using HTTPS

# Ensure session cookies persist
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Optional: Extend session timeout
SESSION_COOKIE_AGE = 1209600  # 2 weeks


LOGIN_REDIRECT_URL = 'spotifyWrapped:initial_login'


# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8000/spotifyWrapped/spotify/callback/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'spotifyWrapped',  # Your app name here
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
