from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsAdmin
from users.api.serializers import RespondentCreateSerializer
from users.models import User


@extend_schema_view(
    post=extend_schema(
        operation_id="respondent_create",
        summary="Criar usuário do tipo respondent",
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
    )
)
class RespondentCreateView(generics.CreateAPIView):
    model = User
    serializer_class = RespondentCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
