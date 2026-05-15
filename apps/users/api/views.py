from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import CustomPagination
from apps.core.permissions import IsAdmin
from apps.users.api.serializers import (
    RespondentCreateSerializer,
    RespondentDetailSerializer,
    RespondentListSerializer,
)
from apps.users.models import User


@extend_schema_view(
    create=extend_schema(
        operation_id="respondent_create",
        summary="Cadastrar respondente",
        description=(
            "Endpoint para cadastrar um novo usuário do tipo `RESPONDENT`. "
            "A requisição deve ser realizada por um usuário autenticado"
            " com perfil `ADMIN`.\n\n"
            "O usuário será criado utilizando apenas o e-mail informado. "
            "Uma senha será gerada automaticamente pelo sistema e enviada para"
            " o e-mail do usuário.\n\n"
        ),
        request=RespondentCreateSerializer,
        responses={
            201: OpenApiResponse(description="Usuário criado com sucesso."),
            400: OpenApiResponse(
                description="Dados inválidos fornecidos na requisição."
            ),
            401: OpenApiResponse(description="Usuário não autenticado."),
            403: OpenApiResponse(
                description=(
                    "Permissão negada. "
                    "Apenas administradores podem acessar este endpoint."
                )
            ),
        },
        tags=["respondents"],
    ),
    list=extend_schema(
        operation_id="respondent_list",
        summary=_("Listar todos os respondentes"),
        description=_("Retorna todos os respondentes cadastrados pelo administrador"),
    ),
    retrieve=extend_schema(
        operation_id="respondent_detail",
        summary=_("Detalhar respondente específico"),
        description=_("Retorna os detalhes de um respondente específico"),
    ),
    update=extend_schema(
        operation_id="respondent_update",
        summary=_("Atualizar respondente (completamente)"),
        description=_("Atualiza todos os campos de um respondente"),
    ),
    partial_update=extend_schema(
        operation_id="respondent_partial_update",
        summary=_("Atualizar respondente (parcialmente)"),
        description=_("Atualiza somente os campos enviados de um respondente"),
    ),
    destroy=extend_schema(
        operation_id="respondent_delete",
        summary=_("Apagar respondente"),
        description=_("Apaga um respondente do banco de dados"),
    ),
    activate=extend_schema(
        operation_id="respondent_activate",
        summary=_("Ativar respondente"),
        description=_("Ativa a conta de um respondente específico"),
        request=None,
        responses={
            204: None,
            404: OpenApiResponse(description=_("Respondente não encontrado")),
        },
    ),
    deactivate=extend_schema(
        operation_id="respondent_deactivate",
        summary=_("Desativar respondente"),
        description=_("Desativa a conta de um respondente específico"),
        request=None,
        responses={
            204: None,
            404: OpenApiResponse(description=_("Respondente não encontrado")),
        },
    ),
)
class RespondentViewSet(viewsets.ModelViewSet):
    model = User
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RespondentDetailSerializer

        if self.action == "create":
            return RespondentCreateSerializer

        return RespondentListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()

        return User.objects.filter(created_by=self.request.user)

    @action(
        methods=["post"],
        detail=True,
        url_name="activate",
        url_path="activate",
        serializer_class=None,
    )
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["post"],
        detail=True,
        url_name="deactivate",
        url_path="deactivate",
        serializer_class=None,
    )
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
