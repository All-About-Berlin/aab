from django.core.exceptions import ValidationError as DjangoValidationError
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
from forms.serializers import (
    CitizenshipFeedbackSerializer,
    ImmigrationOfficeLawsuitSerializer,
    PensionRefundQuestionSerializer,
    PensionRefundReminderSerializer,
    PensionRefundRequestSerializer,
    PlaceSuggestionSerializer,
    PublicCitizenshipFeedbackSerializer,
    PublicResidencePermitFeedbackSerializer,
    ResidencePermitFeedbackSerializer,
    TaxIdRequestFeedbackReminderSerializer,
)
from forms.utils import readable_date_range, readable_duration, subscribe_to_newsletter
from django.db.models import F
from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.serializers import as_serializer_error
from rest_framework.views import APIView, exception_handler as drf_exception_handler
from rest_framework.response import Response
from typing import Any
import logging


logger = logging.getLogger(__name__)


class NewsletterSignupView(APIView):
    """
    Proxy the Buttondown API
    """

    def post(self, request):
        email = request.data.get("email")
        ip = request.META.get("HTTP_X_REAL_IP")

        if not email:
            return Response(status=400)

        buttondown_response = subscribe_to_newsletter(email, ip, source="NewsletterSignupView")

        if buttondown_response.status_code == 400:
            return Response(buttondown_response.json(), status=400)

        buttondown_response.raise_for_status()
        return Response(status=200)


class MessagePermission(permissions.BasePermission):
    """
    Messages can be posted anonymously, but only read by admins
    """

    def has_permission(self, request, view):
        if request.method in ("POST", "PUT"):
            return True
        elif request.method == "GET":
            return request.user and request.user.is_superuser
        return False


class NewsletterSubscriptionMixin:
    """
    Mixin for viewsets that accept an optional `subscribe_to_newsletter` parameter.
    When true, subscribes the submitted email address to the newsletter.
    """

    def _maybe_subscribe_to_newsletter(self, request, email):
        if request.data.get("subscribe_to_newsletter") and email:
            ip = request.META.get("HTTP_X_REAL_IP")
            try:
                subscribe_to_newsletter(email, ip, source=type(self).__name__)
            except Exception:
                logger.exception(f"Failed to subscribe {email} to newsletter")

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._maybe_subscribe_to_newsletter(self.request, serializer.instance.email)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._maybe_subscribe_to_newsletter(self.request, serializer.instance.email)


class MessageViewSet(
    NewsletterSubscriptionMixin, mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    http_method_names = ["get", "post"]
    permission_classes = [MessagePermission]


class FeedbackPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "DELETE":
            return request.user and request.user.is_superuser
        return True


class FeedbackViewSet(NewsletterSubscriptionMixin, viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [FeedbackPermission]


class PensionRefundQuestionViewSet(MessageViewSet):
    queryset = PensionRefundQuestion.objects.all()
    serializer_class = PensionRefundQuestionSerializer


class PensionRefundReminderViewSet(MessageViewSet):
    queryset = PensionRefundReminder.objects.all()
    serializer_class = PensionRefundReminderSerializer


class PensionRefundRequestViewSet(MessageViewSet):
    queryset = PensionRefundRequest.objects.all()
    serializer_class = PensionRefundRequestSerializer


class ResidencePermitFeedbackViewSet(FeedbackViewSet):
    queryset = ResidencePermitFeedback.objects.all()
    admin_serializer_class = ResidencePermitFeedbackSerializer
    public_serializer_class = PublicResidencePermitFeedbackSerializer
    filter_params = ["residence_permit_type", "department"]

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return self.admin_serializer_class

        if self.request.method == "GET":
            if self.action == "retrieve":
                # Retrieving own records with modification_key
                return self.admin_serializer_class
            else:
                # Retrieving all records
                return self.public_serializer_class

        return self.admin_serializer_class

    def get_queryset(self):
        filters = {
            param: self.request.query_params[param]
            for param in self.filter_params
            if param in self.request.query_params
        }
        if self.action == "list":
            # Filter out useless feedback, but allow retrieving a single item anyway
            filters["first_response_date__isnull"] = False
        queryset = self.queryset.filter(**filters)
        if self.action == "list":
            order_by = self.request.query_params.get("order_by", "modification_date")
            valid_fields = {f.name for f in self.queryset.model._meta.get_fields() if hasattr(f, "name")}
            if order_by not in valid_fields:
                raise DRFValidationError({"order_by": f"Invalid field: {order_by}"})
            queryset = queryset.order_by(F(order_by).desc(nulls_last=True))
        return queryset

    def get_extra_filters(self, request):
        return {param: v for param in self.filter_params if (v := request.query_params.get(param))}

    def get_stats(self, request) -> dict[str, Any]:
        extra_filters = self.get_extra_filters(request)
        order_by = request.query_params.get("order_by")
        return {
            "first_response_date": ResidencePermitFeedback.objects.wait_times(
                column_start="application_date",
                column_end="first_response_date",
                extra_filters=extra_filters,
                order_by=order_by,
            ),
            "appointment_date": ResidencePermitFeedback.objects.wait_times(
                column_start="first_response_date",
                column_end="appointment_date",
                extra_filters=extra_filters,
                order_by=order_by,
            ),
            "pick_up_date": ResidencePermitFeedback.objects.wait_times(
                column_start="appointment_date",
                column_end="pick_up_date",
                extra_filters=extra_filters,
                order_by=order_by,
            ),
            "start_to_finish": ResidencePermitFeedback.objects.wait_times(
                column_start="application_date",
                column_end="pick_up_date",
                extra_filters=extra_filters,
                order_by=order_by,
            ),
        }

    def _add_human_readable_range(self, stats_dict: dict[str, Any]) -> None:
        if stats_dict["percentile_20"] is not None and stats_dict["percentile_80"] is not None:
            stats_dict["readable_range"] = readable_date_range(
                days_1=stats_dict["percentile_20"], days_2=stats_dict["percentile_80"]
            )
            stats_dict["readable_median"] = readable_duration(stats_dict["median"])
            stats_dict["readable_percentile_20"] = readable_duration(stats_dict["percentile_20"])
            stats_dict["readable_percentile_80"] = readable_duration(stats_dict["percentile_80"])
        else:
            stats_dict["readable_range"] = None
            stats_dict["readable_median"] = None
            stats_dict["readable_percentile_20"] = None
            stats_dict["readable_percentile_80"] = None

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data or {}

        response.data["stats"] = self.get_stats(request)

        for stats_subset in response.data["stats"].values():
            self._add_human_readable_range(stats_subset["all_time"])
            self._add_human_readable_range(stats_subset["last_12_months"])
            for monthly_stats in stats_subset["by_month"]:
                self._add_human_readable_range(monthly_stats)

        return response


class CitizenshipFeedbackViewSet(ResidencePermitFeedbackViewSet):
    queryset = CitizenshipFeedback.objects.all()
    admin_serializer_class = CitizenshipFeedbackSerializer
    public_serializer_class = PublicCitizenshipFeedbackSerializer
    filter_params = ["department"]

    def get_stats(self, request):
        extra_filters = self.get_extra_filters(request)
        order_by = request.query_params.get("order_by")
        return {
            "first_response_date": CitizenshipFeedback.objects.wait_times(
                column_start="application_date",
                column_end="first_response_date",
                extra_filters=extra_filters,
                order_by=order_by,
            ),
            "appointment_date": CitizenshipFeedback.objects.wait_times(
                column_start="first_response_date",
                column_end="appointment_date",
                extra_filters=extra_filters,
                order_by=order_by,
            ),
            "start_to_finish": CitizenshipFeedback.objects.wait_times(
                column_start="application_date",
                column_end="appointment_date",
                extra_filters=extra_filters,
                order_by=order_by,
            ),
        }


class PlaceSuggestionPermission(permissions.BasePermission):
    """
    Place suggestions can be posted anonymously, but only managed by admins
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return request.user and request.user.is_superuser


class PlaceSuggestionViewSet(viewsets.ModelViewSet):
    queryset = PlaceSuggestion.objects.all()
    serializer_class = PlaceSuggestionSerializer
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [PlaceSuggestionPermission]


class TaxIdRequestFeedbackReminderViewSet(MessageViewSet):
    queryset = TaxIdRequestFeedbackReminder.objects.all()
    serializer_class = TaxIdRequestFeedbackReminderSerializer


class ImmigrationOfficeLawsuitViewSet(MessageViewSet):
    queryset = ImmigrationOfficeLawsuit.objects.all()
    serializer_class = ImmigrationOfficeLawsuitSerializer


def exception_handler(exc, context):
    """
    Handle ValidationErrors properly so that they return a 400 instead of a 500
    """
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(as_serializer_error(exc))

    return drf_exception_handler(exc, context)
