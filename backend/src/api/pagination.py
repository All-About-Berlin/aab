from rest_framework.pagination import PageNumberPagination as OriginalPageNumberPagination


class PageNumberPagination(OriginalPageNumberPagination):
    page_size_query_param = "count"
    max_page_size = 500

    def get_page_size(self, request):
        # Superusers can request any page size, bypassing max_page_size.
        if request.user.is_superuser:
            requested = request.query_params.get(self.page_size_query_param)
            if requested:
                try:
                    size = int(requested)
                except ValueError:
                    size = 0
                if size > 0:
                    return size
        return super().get_page_size(request)
