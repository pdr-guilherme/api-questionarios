from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import CustomPagination
from apps.core.permissions import HasSurveyAccess, IsRespondent
from apps.surveys.api.serializers import (
    AssignedSurveySerializer,
)
from apps.surveys.models import Survey


@extend_schema_view(
    list=extend_schema(
        tags=["assigned_surveys"],
        operation_id="assigned_survey_list",
        summary=_("Listar questionários atribuídos"),
        description=_(
            "Retorna todos os questionários publicados "
            "acessíveis ao respondente autenticado"
        ),
    ),
    retrieve=extend_schema(
        tags=["assigned_surveys"],
        operation_id="assigned_survey_detail",
        summary=_("Detalhar questionário atribuído"),
        description=_(
            "Retorna os detalhes de um questionário publicado "
            "acessível ao respondente autenticado"
        ),
    ),
)
class AssignedSurveyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssignedSurveySerializer
    permission_classes = [IsAuthenticated, IsRespondent, HasSurveyAccess]
    pagination_class = CustomPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Survey.objects.none()

        qs = Survey.objects.filter(
            respondents=self.request.user, status=Survey.StatusChoices.PUBLISHED
        ).distinct()
        if self.action == "retrieve":
            qs = qs.prefetch_related("questions")
        return qs
