from rest_framework.permissions import BasePermission

from apps.answers.models import SurveyAccess
from apps.users.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.RoleChoices.ADMIN


class IsRespondent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.RoleChoices.RESPONDENT


class HasSurveyAccess(BasePermission):
    def has_object_permission(self, request, view, obj):
        return SurveyAccess.objects.filter(
            survey=obj,
            user=request.user,
        ).exists()
