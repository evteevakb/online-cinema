from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork, Role


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self) -> QuerySet:
        film_works = (
            self.model.objects.prefetch_related("genres", "persons")
            .values("id", "title", "description", "creation_date", "rating", "type")
            .annotate(genres=ArrayAgg("genres__name", distinct=True))
            .annotate(
                actors=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role=Role.ACTOR),
                    distinct=True,
                )
            )
            .annotate(
                directors=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role=Role.DIRECTOR),
                    distinct=True,
                )
            )
            .annotate(
                writers=ArrayAgg(
                    "persons__full_name",
                    filter=Q(personfilmwork__role=Role.WRITER),
                    distinct=True,
                )
            )
        )
        return film_works

    def render_to_response(self, context: dict) -> JsonResponse:
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self) -> dict:
        queryset = self.get_queryset()

        paginator, page, queryset, _ = self.paginate_queryset(
            queryset, self.paginate_by
        )
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, *, object=None):
        return dict(object)
