from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import CustomPagination
from apps.core.permissions import IsAdmin
from apps.surveys.api.serializers import (
    QuestionImageSerializer,
)
from apps.surveys.models import Question, QuestionImage


@extend_schema_view(
    create=extend_schema(
        tags=["question_images"],
        operation_id="question_image_create",
        summary=_("Enviar imagem para questão"),
        description=_("Faz upload de uma imagem e a associa a uma questão específica"),
    ),
    list=extend_schema(
        tags=["question_images"],
        operation_id="question_image_list",
        summary=_("Listar imagens da questão"),
        description=_("Retorna todas as imagens associadas a uma questão específica"),
    ),
    retrieve=extend_schema(
        tags=["question_images"],
        operation_id="question_image_detail",
        summary=_("Detalhar imagem específica"),
        description=_("Retorna os detalhes de uma imagem específica"),
    ),
    update=extend_schema(
        tags=["question_images"],
        operation_id="question_image_update",
        summary=_("Atualizar imagem (completamente)"),
        description=_("Atualiza todos os campos de uma imagem"),
    ),
    partial_update=extend_schema(
        tags=["question_images"],
        operation_id="question_image_partial_update",
        summary=_("Atualizar imagem (parcialmente)"),
        description=_("Atualiza somente os campos enviados de uma imagem"),
    ),
    destroy=extend_schema(
        tags=["question_images"],
        operation_id="question_image_delete",
        summary=_("Apagar imagem"),
        description=_("Apaga uma imagem do banco de dados"),
    ),
)
class QuestionImageViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionImageSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPagination
    parser_classes = [MultiPartParser, JSONParser]

    def get_question(self):
        return get_object_or_404(
            Question,
            pk=self.kwargs["question_pk"],
            survey__author=self.request.user,
        )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return QuestionImage.objects.none()

        return QuestionImage.objects.filter(
            question__survey__author=self.request.user,
            question__pk=self.kwargs["question_pk"],
        )

    def perform_create(self, serializer):
        serializer.save(question=self.get_question())
