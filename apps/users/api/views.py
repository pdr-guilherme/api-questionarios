from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
