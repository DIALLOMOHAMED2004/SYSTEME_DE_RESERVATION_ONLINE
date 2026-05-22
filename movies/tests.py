from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Film, Genre


class MovieListViewTests(TestCase):
    def setUp(self):
        self.genre_action = Genre.objects.create(nom="Action")
        self.genre_drama = Genre.objects.create(nom="Drame")

        Film.objects.create(
            titre="Film noté",
            synopsis="Synopsis 1",
            genre=self.genre_action,
            date_sortie=date(2022, 3, 15),
            duree_minutes=110,
            note_moyenne=Decimal("4.0"),
            nombre_critiques=5,
        )
        Film.objects.create(
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
