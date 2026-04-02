from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.pagination import CustomPagination
from core.permissions import IsAdmin
from surveys.api.serializers import SurveySerializer
from surveys.models import Survey


@extend_schema_view(
    create=extend_schema(
        operation_id="survey_create",
        summary=_("Criar novo questionário"),
        description=_(
            "Cria um novo questionário com base nos dados enviados pelo usuário"
        ),
    ),
    list=extend_schema(
        operation_id="survey_list",
        summary=_("Listar todos os questionários"),
        description=_("Retorna todos os questionários criados por um usuário"),
    ),
    retrieve=extend_schema(
        operation_id="survey_detail",
        summary=_("Detalhar questionário específico"),
        description=_("Retorna os detalhes de um questionário específico"),
    ),
    update=extend_schema(
        operation_id="survey_update",
        summary=_("Atualizar questionário (completamente)"),
        description=_("Atualiza todos os campos de um questionário"),
    ),
    partial_update=extend_schema(
        operation_id="survey_partial_update",
        summary=_("Atualizar questionário (parcialmente)"),
        description=_("Atualiza somente os campos enviados de um questionário"),
    ),
    destroy=extend_schema(
        operation_id="survey_delete",
        summary=_("Apagar questionário"),
        description=_("Apaga um questionário do banco de dados"),
    ),
)
class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Survey.objects.none()

        return Survey.objects.filter(author=self.request.user)
