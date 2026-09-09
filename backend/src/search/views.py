import hashlib
import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from search.pagination import MeilisearchPagination
from search.serializers import HIGHLIGHT_POST_TAG, HIGHLIGHT_PRE_TAG, SearchHitSerializer
from search.services import get_index


logger = logging.getLogger(__name__)

MIN_QUERY_LENGTH = 3
CACHE_TTL_SECONDS = 60


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Search is currently unavailable."
    default_code = "service_unavailable"


class SearchView(GenericAPIView):
    """
    Search API. Returns one page of search results.
    """

    serializer_class = SearchHitSerializer
    pagination_class = MeilisearchPagination

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        page = self.paginator.get_page_number(request)

        if len(query) < MIN_QUERY_LENGTH:
            return Response({"results": [], "page": page, "total_pages": 0, "total_hits": 0})

        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()
        cache_key = f"search:{query_hash}:{page}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        try:
            meili_response = get_index().search(
                query,
                {
                    "page": page,
                    "hitsPerPage": settings.RESULTS_PER_PAGE,
                    "attributesToHighlight": ["title", "body"],
                    "attributesToCrop": ["body"],
                    "cropLength": 30,
                    "highlightPreTag": HIGHLIGHT_PRE_TAG,
                    "highlightPostTag": HIGHLIGHT_POST_TAG,
                },
            )
        except Exception:
            logger.exception("Search failed for query %r", query)
            raise ServiceUnavailable()

        hits = self.paginate_queryset(meili_response)
        serializer = self.get_serializer(hits, many=True)
        response = self.get_paginated_response(serializer.data)
        cache.set(cache_key, response.data, CACHE_TTL_SECONDS)
        return response
