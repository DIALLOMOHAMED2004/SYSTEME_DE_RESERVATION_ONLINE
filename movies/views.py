from django.shortcuts import render


def accueil(request):
    return render(request, "movies/home.html")


def films(request):
    return render(request, "movies/movie_list.html")


def classement(request):
    return render(request, "movies/ranking.html")