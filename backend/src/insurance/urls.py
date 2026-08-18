from django.urls import path, include
from .views import CaseViewSet, HealthInsuranceSignupViewSet
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"case", CaseViewSet)
router.register(r"signup", HealthInsuranceSignupViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
