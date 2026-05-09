from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count, Q


class Genre(models.Model):
    nom = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du genre"
    )

    class Meta:
        ordering = ["nom"]
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    def __str__(self):
        return self.nom


class Acteur(models.Model):
    nom = models.CharField(
        max_length=150,
        verbose_name="Nom de l'acteur"
    )

    class Meta:
        ordering = ["nom"]
        verbose_name = "Acteur"
        verbose_name_plural = "Acteurs"

    def __str__(self):
        return self.nom


class Film(models.Model):
    titre = models.CharField(
        max_length=200,
        verbose_name="Titre"
    )

    synopsis = models.TextField(
        verbose_name="Synopsis"
    )

    genre = models.ForeignKey(
        Genre,
        on_delete=models.PROTECT,
        related_name="films",
        verbose_name="Genre"
    )

    date_sortie = models.DateField(
        verbose_name="Date de sortie"
    )

    duree_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Durée en minutes"
    )

    affiche = models.ImageField(
        upload_to="affiches/",
        blank=True,
        null=True,
        verbose_name="Affiche du film"
    )

    acteurs = models.ManyToManyField(
        Acteur,
        through="Casting",
        related_name="films",
        verbose_name="Casting principal"
    )

    note_moyenne = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Note moyenne"
    )

    nombre_critiques = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Nombre de critiques"
    )

    class Meta:
        ordering = ["titre"]
        verbose_name = "Film"
        verbose_name_plural = "Films"
        indexes = [
            models.Index(fields=["titre"]),
            models.Index(fields=["date_sortie"]),
            models.Index(fields=["note_moyenne"]),
            models.Index(fields=["nombre_critiques"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(duree_minutes__gte=1),
                name="film_duree_positive"
            ),
            models.CheckConstraint(
                condition=(
                    Q(note_moyenne__gte=0) & Q(note_moyenne__lte=5)
                ) | Q(note_moyenne__isnull=True),
                name="film_note_moyenne_entre_0_et_5"
            ),
        ]

    def __str__(self):
        return self.titre

    @property
    def annee_sortie(self):
        return self.date_sortie.year

    def afficher_note(self):
        if self.note_moyenne is None:
            return "Pas encore noté"
        return f"{self.note_moyenne}/5"

    def mettre_a_jour_statistiques(self):
        """
        Met à jour la note moyenne et le nombre de critiques du film.

        Cette méthode respecte la règle du cahier des charges :
        après l'ajout, la modification ou la suppression d'une critique,
        la note moyenne du film doit être mise à jour.
        """
        statistiques = self.critiques.aggregate(
            moyenne=Avg("note"),
            total=Count("id")
        )

        moyenne = statistiques["moyenne"]
        total = statistiques["total"]

        if moyenne is None:
            nouvelle_moyenne = None
        else:
            nouvelle_moyenne = Decimal(str(round(moyenne, 2)))

        Film.objects.filter(pk=self.pk).update(
            note_moyenne=nouvelle_moyenne,
            nombre_critiques=total
        )

        self.note_moyenne = nouvelle_moyenne
        self.nombre_critiques = total


class Casting(models.Model):
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name="castings",
        verbose_name="Film"
    )

    acteur = models.ForeignKey(
        Acteur,
        on_delete=models.CASCADE,
        related_name="castings",
        verbose_name="Acteur"
    )

    class Meta:
        verbose_name = "Casting"
        verbose_name_plural = "Castings"
        constraints = [
            models.UniqueConstraint(
                fields=["film", "acteur"],
                name="casting_film_acteur_unique"
            )
        ]

    def __str__(self):
        return f"{self.acteur} dans {self.film}"


class Critique(models.Model):
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name="critiques",
        verbose_name="Film concerné"
    )

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="critiques",
        verbose_name="Auteur"
    )

    titre = models.CharField(
        max_length=200,
        verbose_name="Titre de la critique"
    )

    texte = models.TextField(
        verbose_name="Texte de la critique"
    )

    note = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        verbose_name="Note sur 5"
    )

    date_publication = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de publication"
    )

    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )

    class Meta:
        ordering = ["-date_publication"]
        verbose_name = "Critique"
        verbose_name_plural = "Critiques"
        constraints = [
            models.UniqueConstraint(
                fields=["film", "utilisateur"],
                name="critique_unique_par_utilisateur_et_film"
            ),
            models.CheckConstraint(
                condition=Q(note__gte=1) & Q(note__lte=5),
                name="critique_note_entre_1_et_5"
            ),
        ]

    def __str__(self):
        return f"{self.titre} - {self.film} par {self.utilisateur}"

    def save(self, **kwargs):
        ancien_film_id = None

        if self.pk:
            ancien_film_id = (
                Critique.objects
                .filter(pk=self.pk)
                .values_list("film_id", flat=True)
                .first()
            )

        super().save(**kwargs)

        self.film.mettre_a_jour_statistiques()

        if ancien_film_id and ancien_film_id != self.film_id:
            ancien_film = Film.objects.filter(pk=ancien_film_id).first()
            if ancien_film:
                ancien_film.mettre_a_jour_statistiques()

    def delete(self, using=None, keep_parents=False):
        film = self.film
        resultat = super().delete(using=using, keep_parents=keep_parents)
        film.mettre_a_jour_statistiques()
        return resultat


class Commentaire(models.Model):
    critique = models.ForeignKey(
        Critique,
        on_delete=models.CASCADE,
        related_name="commentaires",
        verbose_name="Critique concernée"
    )

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commentaires",
        verbose_name="Auteur"
    )

    texte = models.TextField(
        verbose_name="Texte du commentaire"
    )

    date_publication = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de publication"
    )

    class Meta:
        ordering = ["date_publication"]
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    def __str__(self):
        return f"Commentaire de {self.utilisateur} sur {self.critique}"