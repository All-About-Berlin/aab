import hashlib
import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from search.pagination import MeilisearchPagination
from search.serializers import HIGHLIGHT_POST_TAG, HIGHLIGHT_PRE_TAG, SearchHitSerializer
from search.services import CONTENT_INDEX, FORUM_INDEX, get_meili_client


logger = logging.getLogger(__name__)

MIN_QUERY_LENGTH = 3
CACHE_TTL_SECONDS = 60

CONTENT_TYPES = {"docs", "glossary", "guides", "newsletter", "pages", "tools"}
FORUM_TYPE = "forum"


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
        type_filter = (request.query_params.get("type") or "").strip()
        page = self.paginator.get_page_number(request)

        if len(query) < MIN_QUERY_LENGTH:
            return Response({"results": [], "page": page, "total_pages": 0, "total_hits": 0})

        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()
        cache_key = f"search:{query_hash}:{type_filter}:{page}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        per_index_query = {
            "q": query,
            "attributesToHighlight": ["title", "body"],
            "attributesToCrop": ["body"],
            "cropLength": 30,
            "highlightPreTag": HIGHLIGHT_PRE_TAG,
            "highlightPostTag": HIGHLIGHT_POST_TAG,
        }
        queries = []
        if type_filter == FORUM_TYPE:
            queries.append({"indexUid": FORUM_INDEX, **per_index_query})
        elif type_filter in CONTENT_TYPES:
            queries.append({"indexUid": CONTENT_INDEX, "filter": f'type = "{type_filter}"', **per_index_query})
        else:
            queries.append({"indexUid": CONTENT_INDEX, **per_index_query})
            queries.append({"indexUid": FORUM_INDEX, **per_index_query})

        try:
            meili_response = get_meili_client().multi_search(
                queries=queries,
                federation={
                    "limit": settings.RESULTS_PER_PAGE,
                    "offset": (page - 1) * settings.RESULTS_PER_PAGE,
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
