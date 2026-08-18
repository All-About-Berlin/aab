from django_countries.serializers import CountryFieldMixin
from rest_framework.serializers import ModelSerializer
from .models import Case, HealthInsuranceSignup


class CaseSerializer(CountryFieldMixin, ModelSerializer):
    class Meta:
        model = Case
        fields = "__all__"
        read_only_fields = ["site"]


class HealthInsuranceSignupSerializer(CountryFieldMixin, ModelSerializer):
    class Meta:
        model = HealthInsuranceSignup
        fields = "__all__"
        read_only_fields = ["site", "status", "submission_date"]

    def validate(self, attrs):
        instance = HealthInsuranceSignup(**attrs)
        instance.clean()
        return attrs
