from django.urls import path

from .views import (
    ProfileEditView,
    ProfileView,
    RegisterView,
    UserLoginView,
    UserLogoutView,
)

app_name = "accounts"

urlpatterns = [
    path("connexion/", UserLoginView.as_view(), name="connexion"),
    path("inscription/", RegisterView.as_view(), name="inscription"),
    path("deconnexion/", UserLogoutView.as_view(), name="deconnexion"),
    path("profil/", ProfileView.as_view(), name="profil"),
    path("profil/modifier/", ProfileEditView.as_view(), name="modifier_profil"),
]

