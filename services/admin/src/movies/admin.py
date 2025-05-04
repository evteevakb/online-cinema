from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmworkInline,
        PersonFilmworkInline,
    )
    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
    )
    list_filter = (
        "type",
        "genres",
    )
    search_fields = (
        "title",
        "description",
        "id",
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "description",
        "id",
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = (
        "full_name",
        "id",
    )
