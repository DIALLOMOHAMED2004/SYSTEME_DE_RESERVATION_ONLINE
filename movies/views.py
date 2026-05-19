from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Page d'accueil minimale utilisée par les redirections du projet."""

    template_name = "movies/home.html"


class MovieListView(TemplateView):
    """Placeholder du catalogue, conservé pour les liens de navigation."""

    template_name = "movies/movie_list.html"


class RankingView(TemplateView):
    """Placeholder du classement, conservé pour les liens de navigation."""

    template_name = "movies/ranking.html"
