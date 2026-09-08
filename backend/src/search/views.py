import hashlib
import logging

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from search.services import get_index


logger = logging.getLogger(__name__)

MIN_QUERY_LENGTH = 3
CACHE_TTL_SECONDS = 60
MAX_RESULTS = 20


class SearchView(APIView):
    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        if len(query) < MIN_QUERY_LENGTH:
            return Response({"results": []})

        cache_key = "search:forum:" + hashlib.sha256(query.encode("utf-8")).hexdigest()
        cached = cache.get(cache_key)
        if cached is not None:
            return Response({"results": cached})

        try:
            meili_response = get_index().search(
                query,
                {
                    "limit": MAX_RESULTS,
                    "attributesToHighlight": ["title", "body"],
                    "attributesToCrop": ["body"],
                    "cropLength": 30,
                },
            )
        except Exception:
            logger.exception("Search failed for query %r", query)
            return Response({"results": []}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        results = [
            {
                "title": hit.get("_formatted", {}).get("title", hit["title"]),
                "url": hit["url"],
                "category": hit["category"],
                "snippet": hit.get("_formatted", {}).get("body", ""),
            }
            for hit in meili_response.get("hits", [])
        ]
        cache.set(cache_key, results, CACHE_TTL_SECONDS)
        return Response({"results": results})
