from .models import Case
from .serializers import CaseSerializer
from forms.views import MessageViewSet


class CaseViewSet(MessageViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def perform_create(self, serializer):
        serializer.save(site=self.request.get_host())
