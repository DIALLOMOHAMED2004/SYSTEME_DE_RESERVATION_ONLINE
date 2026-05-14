from django.urls import path
from . import views

app_name = "movies"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("films/", views.films, name="films"),
    path("classement/", views.classement, name="classement"),
]