from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import CustomPagination
from apps.core.permissions import IsAdmin
from apps.surveys.api.serializers import (
    OptionSerializer,
)
from apps.surveys.models import Option, Question


@extend_schema_view(
    create=extend_schema(
        tags=["options"],
        operation_id="option_create",
        summary=_("Criar nova opção"),
        description=_("Cria uma nova opção e a associa a uma questão específica"),
    ),
    list=extend_schema(
        tags=["options"],
        operation_id="option_list",
        summary=_("Listar opções da questão"),
        description=_("Retorna todas as opções associadas a uma questão específica"),
    ),
    retrieve=extend_schema(
        tags=["options"],
        operation_id="option_detail",
        summary=_("Detalhar opção específica"),
        description=_("Retorna os detalhes de uma opção específica"),
    ),
    update=extend_schema(
        tags=["options"],
        operation_id="option_update",
        summary=_("Atualizar opção (completamente)"),
        description=_("Atualiza todos os campos de uma opção"),
    ),
    partial_update=extend_schema(
        tags=["options"],
        operation_id="option_partial_update",
        summary=_("Atualizar opção (parcialmente)"),
        description=_("Atualiza somente os campos enviados de uma opção"),
    ),
    destroy=extend_schema(
        tags=["options"],
        operation_id="option_delete",
        summary=_("Apagar opção"),
        description=_("Apaga uma opção do banco de dados"),
    ),
)
class OptionViewSet(viewsets.ModelViewSet):
    serializer_class = OptionSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPagination

    def get_question(self):
        return get_object_or_404(
            Question,
            pk=self.kwargs["question_pk"],
            survey__author=self.request.user,
        )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Option.objects.none()

        return Option.objects.filter(
            question__survey__author=self.request.user,
            question__pk=self.kwargs["question_pk"],
        )

    def perform_create(self, serializer):
        serializer.save(question=self.get_question())
