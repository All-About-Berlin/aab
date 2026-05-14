from django_countries.serializers import CountryFieldMixin
from rest_framework.serializers import ModelSerializer
from .models import Case


class CaseSerializer(CountryFieldMixin, ModelSerializer):
    class Meta:
        model = Case
        fields = "__all__"
        read_only_fields = ["site"]
