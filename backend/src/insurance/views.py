from .models import Case, HealthInsuranceSignup
from .serializers import CaseSerializer, HealthInsuranceSignupSerializer
from forms.views import MessageViewSet


class CaseViewSet(MessageViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def perform_create(self, serializer):
        serializer.save(site=self.request.get_host())
        self._maybe_subscribe_to_newsletter(self.request, serializer.instance.email)


class HealthInsuranceSignupViewSet(MessageViewSet):
    queryset = HealthInsuranceSignup.objects.all()
    serializer_class = HealthInsuranceSignupSerializer

    def perform_create(self, serializer):
        serializer.save(site=self.request.get_host())
        self._maybe_subscribe_to_newsletter(self.request, serializer.instance.email)
