from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class MeilisearchPagination(BasePagination):
    """Wraps an already-paginated Meilisearch response into a DRF pagination envelope."""

    def get_page_number(self, request):
        try:
            page = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            return 1
        return max(page, 1)

    def paginate_queryset(self, queryset, request, view=None):
        self.page = queryset.get("page", 1)
        self.total_pages = queryset.get("totalPages", 0)
        self.total_hits = queryset.get("totalHits", 0)
        return queryset.get("hits", [])

    def get_paginated_response(self, data):
        return Response(
            {
                "results": data,
                "page": self.page,
                "total_pages": self.total_pages,
                "total_hits": self.total_hits,
            }
        )
