from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.answers.api.serializers import (
    RespondentProgressDetailSerializer,
    RespondentProgressListSerializer,
    SurveyProgressDetailSerializer,
    SurveyProgressListSerializer,
)
from apps.answers.models import Submission, SurveyAccess
from apps.core.pagination import CustomPagination
from apps.core.permissions import IsAdmin
from apps.surveys.models import Question, Survey


@extend_schema_view(
    list=extend_schema(
        operation_id="progress_survey_list",
        summary=_("Listar progresso dos questionários"),
        description=_(
            "Retorna todos os questionários do admin com agregações de progresso"
        ),
    ),
    retrieve=extend_schema(
        operation_id="progress_survey_detail",
        summary=_("Detalhar progresso do questionário"),
        description=_(
            "Retorna o progresso detalhado de um questionário com lista de respondentes"
        ),
    ),
)
class SurveyProgressViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SurveyProgressDetailSerializer
        return SurveyProgressListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Survey.objects.none()

        qs = Survey.objects.filter(author=self.request.user)

        if self.action == "list":
            qs = qs.prefetch_related(
                Prefetch(
                    "accesses",
                    queryset=SurveyAccess.objects.select_related("user"),
                ),
                Prefetch(
                    "submissions",
                    queryset=Submission.objects.all(),
                ),
            )

        if self.action == "retrieve":
            qs = qs.prefetch_related(
                "questions",
                Prefetch(
                    "accesses",
                    queryset=SurveyAccess.objects.select_related("user"),
                ),
                Prefetch(
                    "submissions",
                    queryset=Submission.objects.all(),
                ),
            )

        return qs


respondent_viewset_params = {
    "survey_pk": OpenApiParameter(
        name="survey_pk",
        description=_("string UUID que identifica unicamente este questionário"),
        required=True,
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.PATH,
    ),
    "id": OpenApiParameter(
        name="id",
        description=_(
            "string UUID que identifica unicamente um objeto de acesso "
            "usuário-questionário"
        ),
        required=True,
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.PATH,
    ),
}


@extend_schema_view(
    list=extend_schema(
        operation_id="progress_respondent_list",
        summary=_("Listar progresso dos respondentes"),
        description=_(
            "Retorna todos os respondentes vinculados ao questionário "
            "com seu progresso individual"
        ),
        parameters=[respondent_viewset_params["survey_pk"]],
    ),
    retrieve=extend_schema(
        operation_id="progress_respondent_detail",
        summary=_("Detalhar progresso do respondente"),
        description=_(
            "Retorna o progresso detalhado de um respondente, "
            "incluindo todas as questões e respostas"
        ),
        parameters=[
            respondent_viewset_params["survey_pk"],
            respondent_viewset_params["id"],
        ],
    ),
)
class RespondentProgressViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RespondentProgressDetailSerializer
        return RespondentProgressListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SurveyAccess.objects.none()

        qs = SurveyAccess.objects.filter(
            survey__pk=self.kwargs["survey_pk"],
            survey__author=self.request.user,
        ).select_related("user", "survey")

        if self.action == "list":
            qs = qs.prefetch_related(
                Prefetch(
                    "user__submissions",
                    queryset=Submission.objects.filter(
                        survey__pk=self.kwargs["survey_pk"],
                    ).prefetch_related(
                        "answers",
                        "answers__option",
                    ),
                ),
            )

        if self.action == "retrieve":
            qs = qs.prefetch_related(
                Prefetch(
                    "user__submissions",
                    queryset=Submission.objects.filter(
                        survey__pk=self.kwargs["survey_pk"],
                    ).prefetch_related(
                        "answers",
                        "answers__option",
                        "answers__question",
                    ),
                ),
                Prefetch(
                    "survey__questions",
                    queryset=Question.objects.order_by("order"),
                ),
            )

        return qs
