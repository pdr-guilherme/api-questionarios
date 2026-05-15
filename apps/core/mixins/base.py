from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied

from apps.surveys.models import Survey


class SurveyEditableMixin:
    def get_parent_survey(self) -> Survey:
        raise NotImplementedError(
            f"{self.__class__.__name__} deve implementar get_parent_survey()"
        )

    def _check_survey_is_draft(self):
        survey = self.get_parent_survey()
        if survey.status != Survey.StatusChoices.DRAFT:
            raise PermissionDenied(
                _("Não é possível modificar um questionário que não está em rascunho.")
            )

    def perform_create(self, serializer):
        self._check_survey_is_draft()
        super().perform_create(serializer)  # type: ignore

    def perform_update(self, serializer):
        self._check_survey_is_draft()
        super().perform_update(serializer)  # type: ignore

    def perform_destroy(self, instance):
        self._check_survey_is_draft()
        super().perform_destroy(instance)  # type: ignore
