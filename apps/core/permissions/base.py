from rest_framework.permissions import BasePermission

from apps.answers.models import Answer, Submission, SurveyAccess
from apps.users.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.RoleChoices.ADMIN


class IsRespondent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.RoleChoices.RESPONDENT


class HasSurveyAccess(BasePermission):
    def has_object_permission(self, request, view, obj):

        # determina qual é o survey com base no tipo do objeto
        if isinstance(obj, Submission):
            survey = obj.survey
        elif isinstance(obj, Answer):
            survey = obj.submission.survey
        else:
            survey = obj

        return SurveyAccess.objects.filter(
            survey=survey,
            user=request.user,
        ).exists()
