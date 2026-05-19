from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UsernameField,
)
from django.core.exceptions import ValidationError


User = get_user_model()


class RegisterForm(UserCreationForm):
    """Formulaire d'inscription basé sur l'utilisateur Django standard."""

    email = forms.EmailField(
        label="Adresse email",
        required=True,
        help_text="Nous ne partagerons jamais votre email.",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "exemple@email.com",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Votre nom d'utilisateur",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nom d'utilisateur"
        self.fields["username"].help_text = (
            "Votre nom d'utilisateur sera visible publiquement."
        )
        self.fields["password1"].label = "Mot de passe"
        self.fields["password1"].help_text = "Au moins 8 caractères recommandés."
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Votre mot de passe",
            }
        )
        self.fields["password2"].label = "Confirmer le mot de passe"
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Confirmez votre mot de passe",
            }
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """Authentifie un utilisateur avec son nom d'utilisateur ou son email."""

    username = UsernameField(
        label="Nom d'utilisateur ou email",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "class": "form-control",
                "placeholder": "Nom d'utilisateur ou email",
            }
        ),
    )

    error_messages = {
        "invalid_login": (
            "Identifiants incorrects. Veuillez vérifier votre nom d'utilisateur, "
            "votre email et votre mot de passe."
        ),
        "inactive": "Ce compte est inactif.",
    }

    def clean(self):
        identifier = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if identifier is not None and password:
            auth_username = identifier

            if "@" in identifier:
                try:
                    user = User.objects.get(email__iexact=identifier)
                except User.DoesNotExist:
                    pass
                except User.MultipleObjectsReturned:
                    raise self.get_invalid_login_error()
                else:
                    auth_username = user.get_username()

            self.user_cache = authenticate(
                self.request,
                username=auth_username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["password"].label = "Mot de passe"
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Votre mot de passe",
            }
        )


class ProfileUpdateForm(forms.ModelForm):
    """Formulaire de modification des informations personnelles du compte."""

    class Meta:
        model = User
        fields = ("username", "email")
        labels = {
            "username": "Nom d'utilisateur",
            "email": "Adresse email",
        }
        help_texts = {
            "username": "Votre nom d'utilisateur sera visible publiquement.",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        queryset = User.objects.filter(username__iexact=username)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if not email:
            raise ValidationError("L'adresse email est obligatoire.")

        queryset = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email
