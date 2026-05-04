from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.answers.api.serializers import AnswerSerializer
from apps.answers.models import Answer, Submission
from apps.core.permissions import HasSurveyAccess, IsRespondent
from apps.surveys.models import Survey

params = [
    OpenApiParameter(
        name="submission_pk",
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.PATH,
        description=_("UUID do preenchimento"),
    ),
    OpenApiParameter(
        name="id",
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.PATH,
        description=_("UUID da resposta"),
    ),
]


@extend_schema_view(
    list=extend_schema(
        tags=["answers"],
        operation_id="answer_list",
        summary=_("Listar respostas"),
        description=_("Retorna todas as respostas de um preenchimento"),
        parameters=[params[0]],
    ),
    retrieve=extend_schema(
        tags=["answers"],
        operation_id="answer_detail",
        summary=_("Detalhar resposta"),
        description=_("Retorna os detalhes de uma resposta específica"),
        parameters=params,
    ),
    create=extend_schema(
        tags=["answers"],
        operation_id="answer_create",
        summary=_("Enviar resposta"),
        description=_("Envia ou substitui a resposta de uma questão no preenchimento"),
        parameters=params,
        responses={
            201: AnswerSerializer,
            403: OpenApiResponse(description=_("Preenchimento já concluído")),
        },
    ),
    destroy=extend_schema(
        tags=["answers"],
        operation_id="answer_delete",
        summary=_("Apagar resposta"),
        description=_("Apaga a resposta de uma questão do preenchimento"),
        parameters=params,
    ),
)
class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRespondent, HasSurveyAccess]
    serializer_class = AnswerSerializer
    http_method_names = ["get", "post", "delete", "head", "options", "trace"]

    def get_submission(self):
        return get_object_or_404(
            Submission,
            pk=self.kwargs["submission_pk"],
            user=self.request.user,
            survey__respondents=self.request.user,
            survey__status=Survey.StatusChoices.PUBLISHED,
        )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Answer.objects.none()

        submission = self.get_submission()
        return Answer.objects.filter(submission=submission)

    def perform_create(self, serializer):
        submission = self.get_submission()

        if submission.status == Submission.StatusChoices.COMPLETED:
            raise PermissionDenied(
                _("Não é possível modificar um preenchimento já concluído.")
            )

        question = serializer.validated_data["question"]
        option = serializer.validated_data["option"]

        Answer.objects.update_or_create(
            submission=submission,
            question=question,
            defaults={"option": option},
        )
