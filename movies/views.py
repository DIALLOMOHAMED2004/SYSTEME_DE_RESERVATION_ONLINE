from django.contrib import messages
from django.shortcuts import render


def ui_test(request):
    messages.success(
        request,
        "Le socle visuel Movie Review est bien chargé."
    )
    return render(request, "movies/ui_test.html")