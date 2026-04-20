from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.answers.models import SurveyAccess
from apps.core.pagination import CustomPagination
from apps.core.permissions import IsAdmin
from apps.surveys.api.serializers import (
    GrantAccessSerializer,
    SurveySerializer,
)
from apps.surveys.models import Survey
from apps.users.models import User


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
    publish=extend_schema(
        operation_id="survey_publish",
        summary=_("Publicar questionário"),
        description=_("Altera o status do questionário de rascunho para publicado"),
        request=None,
        responses={
            204: None,
            400: OpenApiResponse(description=_("Transição de status inválida")),
        },
    ),
    close=extend_schema(
        operation_id="survey_close",
        summary=_("Encerrar questionário"),
        description=_("Altera o status do questionário de publicado para encerrado"),
        request=None,
        responses={
            204: None,
            400: OpenApiResponse(description=_("Transição de status inválida")),
        },
    ),
    grant_access=extend_schema(
        operation_id="survey_grant_access",
        summary=_("Conceder acesso ao questionário"),
        description=_("Concede acesso a um respondente para responder o questionário"),
        request=GrantAccessSerializer,
        responses={
            204: None,
            400: OpenApiResponse(
                description=_("Usuário inválido ou ausente no payload")
            ),
            404: OpenApiResponse(description=_("Questionário não encontrado")),
        },
    ),
    revoke_access=extend_schema(
        operation_id="survey_revoke_access",
        summary=_("Revogar acesso ao questionário"),
        description=_("Revoga o acesso de um respondente ao questionário"),
        request=GrantAccessSerializer,
        responses={
            204: None,
            400: OpenApiResponse(
                description=_("Usuário inválido ou ausente no payload")
            ),
            404: OpenApiResponse(description=_("Questionário não encontrado")),
        },
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

    @action(
        detail=True,
        methods=["post"],
        url_path="publish",
        url_name="publish",
        serializer_class=None,
    )
    def publish(self, request, pk=None):
        survey = self.get_object()

        try:
            survey.transition_to(Survey.StatusChoices.PUBLISHED)
        except ValidationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path="close",
        url_name="close",
        serializer_class=None,
    )
    def close(self, request, pk=None):
        survey = self.get_object()

        try:
            survey.transition_to(Survey.StatusChoices.CLOSED)
        except ValidationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path="grant-access",
        url_name="grant-access",
    )
    def grant_access(self, request, pk=None):
        survey = self.get_object()
        serializer = GrantAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(pk=serializer.validated_data["user_id"])
        SurveyAccess.objects.get_or_create(survey=survey, user=user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path="revoke-access",
        url_name="revoke-access",
    )
    def revoke_access(self, request, pk=None):
        survey = self.get_object()
        serializer = GrantAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        SurveyAccess.objects.filter(
            survey=survey,
            user_id=serializer.validated_data["user_id"],
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
