from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


User = get_user_model()


@override_settings(
    PASSWORD_HASHERS=[
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
)
class AccountsAuthTests(TestCase):
    """Vérifie les flux principaux de la phase utilisateurs."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="cinephile",
            email="cinephile@example.com",
            password="Motdepasse123!",
        )

    def test_registration_logs_user_in_and_redirects_to_profile(self):
        response = self.client.post(
            reverse("accounts:inscription"),
            {
                "username": "nouveau",
                "email": "nouveau@example.com",
                "password1": "Motdepasse123!",
                "password2": "Motdepasse123!",
            },
        )

        new_user = User.objects.get(username="nouveau")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("accounts:profil"))
        self.assertEqual(str(new_user.pk), self.client.session["_auth_user_id"])

    def test_registration_rejects_duplicate_email(self):
        response = self.client.post(
            reverse("accounts:inscription"),
            {
                "username": "autre",
                "email": "cinephile@example.com",
                "password1": "Motdepasse123!",
                "password2": "Motdepasse123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "email",
            "Cette adresse email est déjà utilisée.",
        )

    def test_login_with_username(self):
        response = self.client.post(
            reverse("accounts:connexion"),
            {
                "username": "cinephile",
                "password": "Motdepasse123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("accounts:profil"))
        self.assertEqual(str(self.user.pk), self.client.session["_auth_user_id"])

    def test_login_with_email(self):
        response = self.client.post(
            reverse("accounts:connexion"),
            {
                "username": "cinephile@example.com",
                "password": "Motdepasse123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("accounts:profil"))
        self.assertEqual(str(self.user.pk), self.client.session["_auth_user_id"])

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse("accounts:connexion"),
            {
                "username": "cinephile",
                "password": "mauvais",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post_and_clears_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:deconnexion"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("movies:accueil"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_anonymous_user_is_redirected_from_profile(self):
        response = self.client.get(reverse("accounts:profil"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:connexion')}?next={reverse('accounts:profil')}",
        )

    def test_profile_update_changes_username_and_email(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:modifier_profil"),
            {
                "username": "cinephile_modifie",
                "email": "modifie@example.com",
                "old_password": "",
                "new_password1": "",
                "new_password2": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "cinephile_modifie")
        self.assertEqual(self.user.email, "modifie@example.com")

    def test_password_change_updates_password_and_keeps_user_logged_in(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:modifier_profil"),
            {
                "username": "cinephile",
                "email": "cinephile@example.com",
                "old_password": "Motdepasse123!",
                "new_password1": "NouveauMotdepasse123!",
                "new_password2": "NouveauMotdepasse123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NouveauMotdepasse123!"))

        profile_response = self.client.get(reverse("accounts:profil"))
        self.assertEqual(profile_response.status_code, 200)

    def test_navbar_changes_with_authentication_state(self):
        anonymous_response = self.client.get(reverse("accounts:connexion"))
        self.assertContains(anonymous_response, "Connexion")
        self.assertContains(anonymous_response, "Inscription")
        self.assertNotContains(anonymous_response, "Déconnexion")

        self.client.force_login(self.user)
        authenticated_response = self.client.get(reverse("accounts:profil"))
        self.assertContains(authenticated_response, "Profil")
        self.assertContains(authenticated_response, "Déconnexion")
        self.assertNotContains(authenticated_response, "Inscription")
