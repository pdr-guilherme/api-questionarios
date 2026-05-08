from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.answers.models import Submission


class SubmissionIsEditable(BasePermission):
    message = _("Não é possível modificar um preenchimento já concluído.")

    def has_permission(self, request, view):
        submission_id = view.kwargs.get("submission_pk")

        submission = get_object_or_404(Submission, pk=submission_id)
        if (
            submission.status == Submission.StatusChoices.COMPLETED
            and request.method not in SAFE_METHODS
        ):
            return False

        return True
