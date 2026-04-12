from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import CustomPagination
from apps.core.permissions import IsAdmin
from apps.surveys.api.serializers import (
    OptionSerializer,
    QuestionDetailSerializer,
    QuestionImageSerializer,
    QuestionSerializer,
    SurveySerializer,
)
from apps.surveys.models import Option, Question, QuestionImage, Survey


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

        qs = Survey.objects.filter(author=self.request.user)
        if self.action == "retrieve":
            qs = qs.prefetch_related("questions")
        return qs


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
