import requests
from requests import request

import spotifyWrapped.settings
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import RedirectView
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.utils import timezone


from .models import Choice, Question

class SpotifyLoginView(View):
    def get(self, request):
        spotify_auth_url = 'https://accounts.spotify.com/authorize'
        response_type = 'code'
        scope = 'user-top-read'

        # Construct the Spotify authorization URL
        auth_url = (
            f"{spotify_auth_url}?client_id={spotifyWrapped.settings.SPOTIFY_CLIENT_ID}"
            f"&response_type={response_type}"
            f"&redirect_uri={spotifyWrapped.settings.SPOTIFY_REDIRECT_URI}"
            f"&scope={scope}"
        )


        # Redirect the user to the Spotify authorization page
        return redirect(auth_url)

class SpotifyCallbackView(View):
    def get(self, request):
        auth_code = request.GET.get("code")
        url = "https://accounts.spotify.com/api/token"

        # Headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Data payload
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": spotifyWrapped.settings.SPOTIFY_REDIRECT_URI,
            "client_id": spotifyWrapped.settings.SPOTIFY_CLIENT_ID,
            "client_secret": spotifyWrapped.settings.SPOTIFY_CLIENT_SECRET,
        }

        # Make the POST request
        response = requests.post(url, data=data)

        # Check if the request was successful and print the token
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")  # Only if using auth code flow

            # Save tokens to session
            request.session['access_token'] = access_token
            if refresh_token:
                request.session['refresh_token'] = refresh_token

            # fetch user data
            profile_url = "https://api.spotify.com/v1/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(profile_url, headers=headers)
            profile_data = profile_response.json()

            #save username to session
            request.session['spotify_username'] = profile_data.get("display_name")
            #Uncomment next line for debugging
            #print(profile_data)
        # Redirect to the top songs view or home page after successful authentication
        return redirect("spotifyWrapped:home")

class IndexView(generic.ListView):
    template_name = "spotifyWrapped/initialLogIn.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
               :5
               ]

class HomeView(View):
    template_name = 'spotifyWrapped/home.html'
    def get(self, request):
        username = request.session.get("spotify_username", "Guest")
        return render(request, "spotifyWrapped/home.html", {"username": username})


class DetailView(generic.DetailView):
    model = Question
    template_name = "spotifyWrapped/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "spotifyWrapped/results.html"

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "spotifyWrapped/index.html", context)
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "spotifyWrapped/detail.html", {"question": question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "spotifyWrapped/results.html", {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "spotifyWrapped/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("spotifyWrapped:results", args=(question.id,)))