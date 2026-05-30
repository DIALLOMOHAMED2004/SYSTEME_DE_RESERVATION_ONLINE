from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Film, Genre


class MovieListViewTests(TestCase):
    def setUp(self):
        self.genre_action = Genre.objects.create(nom="Action")
        self.genre_drama = Genre.objects.create(nom="Drame")

        self.film_note = Film.objects.create(
            titre="Film noté",
            synopsis="Synopsis 1",
            genre=self.genre_action,
            date_sortie=date(2022, 3, 15),
            duree_minutes=110,
            note_moyenne=Decimal("4.0"),
            nombre_critiques=5,
        )
        self.film_sans_note = Film.objects.create(
            titre="Film sans note",
            synopsis="Synopsis 2",
            genre=self.genre_drama,
            date_sortie=date(2021, 7, 10),
            duree_minutes=95,
            note_moyenne=None,
            nombre_critiques=0,
        )

    def test_films_page_displays_all_films(self):
        response = self.client.get(reverse("movies:films"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Film noté")
        self.assertContains(response, "Film sans note")
        self.assertContains(response, "Catalogue de Films")

    def test_films_page_filters_by_genre_and_note_min(self):
        response = self.client.get(reverse("movies:films"), {"genre": self.genre_action.id, "note_min": "3"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Film noté")
        self.assertNotContains(response, "Film sans note")
        self.assertContains(response, "1 film")

    def test_films_page_filters_by_genre(self):
        response = self.client.get(reverse("movies:films"), {"genre": self.genre_drama.id})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Film noté")
        self.assertContains(response, "Film sans note")

    def test_films_page_filters_by_year(self):
        response = self.client.get(reverse("movies:films"), {"annee": "2022"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Film noté")
        self.assertNotContains(response, "Film sans note")

    def test_films_page_filters_by_note_min(self):
        response = self.client.get(reverse("movies:films"), {"note_min": "4"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Film noté")
        self.assertNotContains(response, "Film sans note")

    def test_films_page_filters_by_combined_criteria(self):
        response = self.client.get(
            reverse("movies:films"),
            {"genre": self.genre_action.id, "annee": "2022", "note_min": "4"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Film noté")
        self.assertNotContains(response, "Film sans note")
        self.assertContains(response, "1 film")

    def test_films_page_ignores_invalid_filters(self):
        response = self.client.get(
            reverse("movies:films"),
            {"genre": "999", "annee": "1900", "note_min": "9"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Film noté")
        self.assertContains(response, "Film sans note")
        self.assertEqual(response.context["selected_genre"], "")
        self.assertEqual(response.context["selected_annee"], "")
        self.assertEqual(response.context["selected_note_min"], "")

    def test_films_page_displays_empty_state(self):
        response = self.client.get(
            reverse("movies:films"),
            {"genre": self.genre_drama.id, "note_min": "4"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Film noté")
        self.assertNotContains(response, "Film sans note")
        self.assertContains(response, "Aucun film ne correspond aux filtres")

    def test_films_page_contains_detail_link(self):
        response = self.client.get(reverse("movies:films"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("movies:film_detail", args=[self.film_note.pk]))
