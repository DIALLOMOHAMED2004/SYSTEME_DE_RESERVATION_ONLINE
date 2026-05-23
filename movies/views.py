from datetime import date
from decimal import Decimal, InvalidOperation

from django.views.generic import DetailView, TemplateView

from .models import Film, Genre


class HomeView(TemplateView):
    """Page d'accueil minimale utilisée par les redirections du projet."""

    template_name = "movies/home.html"


class MovieListView(TemplateView):
    """Catalogue de films avec filtres par genre, année et note minimale."""

    template_name = "movies/movie_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        films = Film.objects.select_related("genre").all()
        genres = Genre.objects.all()
        annees = [date.year for date in Film.objects.dates("date_sortie", "year", order="DESC")]

        selected_genre = self.request.GET.get("genre", "").strip()
        selected_annee = self.request.GET.get("annee", "").strip()
        selected_note_min = self.request.GET.get("note_min", "").strip()

        if selected_genre.isdigit():
            films = films.filter(genre_id=int(selected_genre))

        if selected_annee.isdigit():
            films = films.filter(date_sortie__year=int(selected_annee))

        if selected_note_min:
            try:
                note_valeur = Decimal(selected_note_min)
            except (InvalidOperation, ValueError):
                note_valeur = None
            else:
                films = films.filter(note_moyenne__gte=note_valeur)

        context.update({
            "films": films,
            "genres": genres,
            "annees": annees,
            "nombre_films": films.count(),
            "selected_genre": selected_genre,
            "selected_annee": selected_annee,
            "selected_note_min": selected_note_min,
        })
        return context


class FilmDetailView(DetailView):
    """Page de détail minimale d'un film, accessible depuis le catalogue."""

    model = Film
    template_name = "movies/movie_detail.html"


class RankingView(TemplateView):
    """Placeholder du classement, conservé pour les liens de navigation."""

    template_name = "movies/ranking.html"