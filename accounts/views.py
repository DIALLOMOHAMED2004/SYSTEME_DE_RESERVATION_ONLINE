from django.shortcuts import render


def connexion(request):
    return render(request, "accounts/login.html")


def inscription(request):
    return render(request, "accounts/register.html")


def profil(request):
    return render(request, "accounts/profile.html")