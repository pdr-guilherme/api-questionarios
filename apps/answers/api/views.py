from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.answers.api.serializers import (
    AnswerSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer,
)
from apps.answers.models import Answer, Submission
from apps.core.pagination import CustomPagination
from apps.core.permissions import HasSurveyAccess, IsRespondent
from apps.surveys.models import Survey


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
                {"detail": _("Não é possível apagar uma submission já concluída.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)


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
        submission = self.get_submission()
        return Answer.objects.filter(submission=submission)

    def perform_create(self, serializer):
        submission = self.get_submission()

        if submission.status == Submission.StatusChoices.COMPLETED:
            raise PermissionDenied(
                _("Não é possível modificar uma submission já concluída.")
            )

        question = serializer.validated_data["question"]
        option = serializer.validated_data["option"]

        Answer.objects.update_or_create(
            submission=submission,
            question=question,
            defaults={"option": option},
        )
