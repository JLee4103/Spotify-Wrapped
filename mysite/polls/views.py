import requests
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import RedirectView
from django.conf import settings
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone


from .models import Choice, Question

class IndexView(generic.ListView):
    template_name = "polls/initialLogIn.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
               :5
               ]

    def spotify_login(request):
        spotify_auth_url = 'https://accounts.spotify.com/authorize'
        response_type = 'code'
        scope = 'user-read-email user-read-private'  # Customize the scope as needed

        auth_url = (
            f"{spotify_auth_url}?client_id={settings.SPOTIFY_CLIENT_ID}"
            f"&response_type={response_type}"
            f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
            f"&scope={scope}"
        )
        return redirect(auth_url)

    def spotify_callback(request):
        code = request.GET.get('code')
        token_url = 'https://accounts.spotify.com/api/token'

        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
            'client_id': settings.SPOTIFY_CLIENT_ID,
            'client_secret': settings.SPOTIFY_CLIENT_SECRET,
        }

        response = requests.post(token_url, data=payload)
        response_data = response.json()

        access_token = response_data.get('access_token')
        refresh_token = response_data.get('refresh_token')

        # Store tokens in session or database
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token

        # Redirect to a page where you use the token to interact with the Spotify API
        return redirect('some_view_using_spotify_api')

    def some_view_using_spotify_api(request):
        access_token = request.session.get('access_token')

        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            profile_url = 'https://api.spotify.com/v1/me'
            response = requests.get(profile_url, headers=headers)
            profile_data = response.json()

            return render(request, 'profile.html', {'profile': profile_data})
        else:
            return redirect('spotify_login')


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
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
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))