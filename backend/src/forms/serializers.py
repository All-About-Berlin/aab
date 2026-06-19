from django_countries.serializers import CountryFieldMixin
from forms.models import (
    CitizenshipFeedback,
    ImmigrationOfficeLawsuit,
    PensionRefundQuestion,
    PensionRefundReminder,
    PensionRefundRequest,
    PlaceSuggestion,
    ResidencePermitFeedback,
    TaxIdRequestFeedbackReminder,
)
from rest_framework.serializers import ModelSerializer, IntegerField, CharField, DateTimeField


class PensionRefundQuestionSerializer(CountryFieldMixin, ModelSerializer):
    status = IntegerField(read_only=True)

    class Meta:
        model = PensionRefundQuestion
        fields = "__all__"


class PensionRefundReminderSerializer(CountryFieldMixin, ModelSerializer):
    status = IntegerField(read_only=True)

    class Meta:
        model = PensionRefundReminder
        fields = "__all__"


class PensionRefundRequestSerializer(CountryFieldMixin, ModelSerializer):
    status = IntegerField(read_only=True)

    class Meta:
        model = PensionRefundRequest
        fields = "__all__"


class ResidencePermitFeedbackSerializer(ModelSerializer):
    modification_key = CharField(read_only=True)
    modification_date = DateTimeField(read_only=True)

    def validate(self, attrs):
        instance = ResidencePermitFeedback(**attrs)
        instance.clean()
        return attrs

    class Meta:
        model = ResidencePermitFeedback
        fields = "__all__"


class PublicResidencePermitFeedbackSerializer(ModelSerializer):
    class Meta:
        model = ResidencePermitFeedback
        exclude = ("email", "modification_key")


class CitizenshipFeedbackSerializer(ModelSerializer):
    modification_key = CharField(read_only=True)
    modification_date = DateTimeField(read_only=True)

    def validate(self, attrs):
        instance = CitizenshipFeedback(**attrs)
        instance.clean()
        return attrs

    class Meta:
        model = CitizenshipFeedback
        fields = "__all__"


class PublicCitizenshipFeedbackSerializer(ModelSerializer):
    class Meta:
        model = CitizenshipFeedback
        exclude = ("email", "modification_key")


class PlaceSuggestionSerializer(ModelSerializer):
    class Meta:
        model = PlaceSuggestion
        fields = "__all__"


class TaxIdRequestFeedbackReminderSerializer(ModelSerializer):
    status = IntegerField(read_only=True)

    class Meta:
        model = TaxIdRequestFeedbackReminder
        fields = "__all__"


class ImmigrationOfficeLawsuitSerializer(ModelSerializer):
    class Meta:
        model = ImmigrationOfficeLawsuit
        fields = "__all__"
