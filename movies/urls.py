from django.urls import path

from .views import HomeView, MovieListView, RankingView

app_name = "movies"

urlpatterns = [
    path("", HomeView.as_view(), name="accueil"),
    path("films/", MovieListView.as_view(), name="films"),
    path("classement/", RankingView.as_view(), name="classement"),
]