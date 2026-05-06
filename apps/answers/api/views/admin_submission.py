from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.answers.api.serializers import (
    AdminSubmissionDetailSerializer,
    AdminSubmissionListSerializer,
)
from apps.answers.filters import AdminSubmissionFilter
from apps.answers.models import Submission
from apps.core.pagination import CustomPagination
from apps.core.permissions import IsAdmin


@extend_schema_view(
    list=extend_schema(
        operation_id="admin_submission_list",
        summary=_("Listar preenchimentos"),
        description=_("Retorna todos os preenchimentos de todos os respondentes"),
    ),
    retrieve=extend_schema(
        operation_id="admin_submission_detail",
        summary=_("Detalhar preenchimento"),
        description=_(
            "Retorna os detalhes de um preenchimento incluindo todas as respostas"
        ),
    ),
)
class AdminSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = CustomPagination
    filterset_class = AdminSubmissionFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AdminSubmissionDetailSerializer
        return AdminSubmissionListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Submission.objects.none()

        qs = (
            Submission.objects.filter(survey__author=self.request.user)
            .select_related("user", "survey")
            .order_by("-started_at")
        )

        if self.action == "retrieve":
            qs = qs.prefetch_related(
                "answers",
                "answers__question",
                "answers__option",
            )
        return qs
