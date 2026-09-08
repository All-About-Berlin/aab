from django.urls import path

from search.views import SearchView


urlpatterns = [
    path("", SearchView.as_view(), name="search"),
]
