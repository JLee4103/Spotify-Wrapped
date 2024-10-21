from django.urls import path
from .views import register, login, logout, default_redirect

app_name = 'restaurantAuth'  # This is the namespace

urlpatterns = [
    path('', default_redirect, name='default_redirect'),  # Redirects 'auth/' to registration
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]