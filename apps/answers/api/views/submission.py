from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.answers.api.serializers import (
    SubmissionDetailSerializer,
    SubmissionListSerializer,
)
from apps.answers.models import Submission
from apps.core.pagination import CustomPagination
from apps.core.permissions import HasSurveyAccess, IsRespondent


@extend_schema_view(
    list=extend_schema(
        tags=["submissions"],
        operation_id="submission_list",
        summary=_("Listar preenchimentos"),
        description=_("Retorna todos os preenchimentos do respondente autenticado"),
    ),
    retrieve=extend_schema(
        tags=["submissions"],
        operation_id="submission_detail",
        summary=_("Detalhar preenchimento"),
        description=_(
            "Retorna os detalhes de um preenchimento, incluindo as respostas"
        ),
    ),
    create=extend_schema(
        tags=["submissions"],
        operation_id="submission_create",
        summary=_("Iniciar preenchimento"),
        description=_("Inicia um novo preenchimento para um questionário publicado"),
    ),
    destroy=extend_schema(
        tags=["submissions"],
        operation_id="submission_delete",
        summary=_("Apagar preenchimentos"),
        description=_(
            "Apaga um preenchimentos em rascunho."
            " Preenchimentos concluídos não podem ser apagados"
        ),
        responses={
            204: None,
            403: OpenApiResponse(description=_("Preenchimento já concluído")),
        },
    ),
    submit=extend_schema(
        tags=["submissions"],
        operation_id="submission_submit",
        summary=_("Enviar preenchimento"),
        description=_(
            "Tenta concluir o preenchimento verificando se todas as "
            "questões obrigatórias foram respondidas"
        ),
        request=None,
        responses={
            200: SubmissionDetailSerializer,
            400: OpenApiResponse(description=_("Preenchimento já concluído")),
            422: OpenApiResponse(
                description=_("Existem questões obrigatórias sem resposta")
            ),
        },
    ),
)
class SubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRespondent, HasSurveyAccess]
    pagination_class = CustomPagination
    http_method_names = ["get", "post", "delete", "head", "options", "trace"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SubmissionDetailSerializer
        return SubmissionListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Submission.objects.none()

        qs = Submission.objects.filter(user=self.request.user)
        if self.action == "retrieve":
            qs = qs.prefetch_related("answers")
        return qs

    def destroy(self, request, *args, **kwargs):
        submission = self.get_object()

        if submission.status == Submission.StatusChoices.COMPLETED:
            return Response(
                {"detail": _("Não é possível apagar um preenchimento já concluído.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_name="submit", url_path="submit")
    def submit(self, request, pk=None):
        submission = self.get_object()

        if submission.status == Submission.StatusChoices.COMPLETED:
            return Response(
                {"detail": _("Este preenchimento já foi concluído.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answered_question_ids = set(
            submission.answers.values_list("question_id", flat=True)
        )
        unanswered_required = (
            submission.survey.questions.filter(is_required=True)
            .exclude(id__in=answered_question_ids)
            .values("id", "text", "order")
        )

        if unanswered_required.exists():
            return Response(
                {
                    "detail": _("Existem questões obrigatórias sem resposta."),
                    "unanswered_questions": list(unanswered_required),
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        submission.try_complete()
        submission.refresh_from_db()

        serializer = self.get_serializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)
