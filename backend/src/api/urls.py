from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path("api/forms/", include("forms.urls")),
    path("api/insurance/", include("insurance.urls")),
    path("", include("forum.urls")),
    path("admin/", admin.site.urls),
]
