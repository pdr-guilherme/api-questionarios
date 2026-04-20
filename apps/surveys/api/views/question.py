from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import CustomPagination
from apps.core.permissions import IsAdmin
from apps.surveys.api.serializers import (
    QuestionDetailSerializer,
    QuestionSerializer,
)
from apps.surveys.models import Question


@extend_schema_view(
    create=extend_schema(
        operation_id="question_create",
        summary=_("Criar nova questão"),
        description=_("Cria uma nova questão com base nos dados enviados pelo usuário"),
    ),
    list=extend_schema(
        operation_id="question_list",
        summary=_("Listar todas as questões"),
        description=_("Retorna todas as questões criadas por um usuário"),
    ),
    retrieve=extend_schema(
        operation_id="question_detail",
        summary=_("Detalhar questão específica"),
        description=_(
            "Retorna os detalhes de uma questão específica, incluindo opções e imagens"
        ),
    ),
    update=extend_schema(
        operation_id="question_update",
        summary=_("Atualizar questão (completamente)"),
        description=_("Atualiza todos os campos de uma questão"),
    ),
    partial_update=extend_schema(
        operation_id="question_partial_update",
        summary=_("Atualizar questão (parcialmente)"),
        description=_("Atualiza somente os campos enviados de uma questão"),
    ),
    destroy=extend_schema(
        operation_id="question_delete",
        summary=_("Apagar questão"),
        description=_("Apaga uma questão do banco de dados"),
    ),
)
class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Question.objects.none()

        qs = Question.objects.filter(survey__author=self.request.user)
        if self.action == "retrieve":
            qs.prefetch_related("options").prefetch_related("images")
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return QuestionDetailSerializer
        return QuestionSerializer
