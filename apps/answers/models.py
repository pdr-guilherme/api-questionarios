from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDPrimaryKeyModel
from apps.surveys.models import Survey
from apps.users.models import User


class SurveyAccess(UUIDPrimaryKeyModel):
    survey = models.ForeignKey(
        Survey,
        verbose_name=_("survey"),
        related_name="accesses",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        related_name="accesses",
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.RoleChoices.RESPONDENT},
    )
    granted_at = models.DateTimeField(_("granted at"), auto_now_add=True)

    class Meta:
        db_table = "survey_accesses"
        verbose_name = _("survey access")
        verbose_name_plural = _("survey accesses")
        ordering = ["survey", "user"]

        constraints = [
            models.UniqueConstraint(
                fields=["survey", "user"],
                name="unique_survey_user_access",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.survey} ({self.granted_at:%Y-%m-%d})"
