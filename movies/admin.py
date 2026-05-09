from django.contrib import admin

from .models import Genre, Acteur, Film, Casting, Critique, Commentaire


class CastingInline(admin.TabularInline):
    model = Casting
    extra = 1


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(Acteur)
class ActeurAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = (
        "titre",
        "genre",
        "date_sortie",
        "duree_minutes",
        "note_moyenne",
        "nombre_critiques",
    )
    list_filter = ("genre", "date_sortie")
    search_fields = ("titre", "synopsis")
    readonly_fields = ("note_moyenne", "nombre_critiques")
    inlines = [CastingInline]


@admin.register(Critique)
class CritiqueAdmin(admin.ModelAdmin):
    list_display = (
        "titre",
        "film",
        "utilisateur",
        "note",
        "date_publication",
        "date_modification",
    )
    list_filter = ("note", "date_publication")
    search_fields = ("titre", "texte", "film__titre", "utilisateur__username")
    readonly_fields = ("date_publication", "date_modification")


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = (
        "critique",
        "utilisateur",
        "date_publication",
    )
    list_filter = ("date_publication",)
    search_fields = ("texte", "utilisateur__username", "critique__titre")
    readonly_fields = ("date_publication",)