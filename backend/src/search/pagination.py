from math import ceil

from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class MeilisearchPagination(BasePagination):
    def get_page_number(self, request):
        try:
            page = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            return 1
        return max(page, 1)

    def paginate_queryset(self, queryset, request, view=None):
        limit = queryset.get("limit", 0) or 1
        offset = queryset.get("offset", 0)
        self.page = offset // limit + 1
        self.total_hits = queryset.get("estimatedTotalHits", 0)
        self.total_pages = ceil(self.total_hits / limit)
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
