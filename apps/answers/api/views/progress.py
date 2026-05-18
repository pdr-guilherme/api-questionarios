from django.db.models import Prefetch
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
