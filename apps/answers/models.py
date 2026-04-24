from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, UUIDPrimaryKeyModel
from apps.surveys.models import Option, Question, Survey
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


class Submission(UUIDPrimaryKeyModel, TimeStampedModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", _("rascunho")
        COMPLETED = "completed", _("concluído")

    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    survey = models.ForeignKey(
        Survey,
        verbose_name=_("survey"),
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    status = models.CharField(
        _("status"),
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    started_at = models.DateTimeField(_("started at"), auto_now_add=True)
    finished_at = models.DateTimeField(_("finished at"), null=True, blank=True)

    VALID_TRANSITIONS = {
        StatusChoices.DRAFT: [StatusChoices.COMPLETED],
        StatusChoices.COMPLETED: [],
    }

    class Meta:
        db_table = "submissions"
        verbose_name = _("submission")
        verbose_name_plural = _("submissions")
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "survey"],
                name="unique_user_survey_submission",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.survey} ({self.status})"

    def transition_to(self, new_status: StatusChoices):
        allowed = self.VALID_TRANSITIONS.get(self.StatusChoices(self.status), [])
        if new_status not in allowed:
            raise ValidationError(f"Transição inválida: {self.status} → {new_status}")
        self.status = new_status
        self.save()

    def try_complete(self):
        required_question_ids = set(
            self.survey.questions.filter(is_required=True).values_list("id", flat=True)
        )
        answered_question_ids = set(self.answers.values_list("question_id", flat=True))
        if required_question_ids.issubset(answered_question_ids):
            self.finished_at = timezone.now()
            self.transition_to(self.StatusChoices.COMPLETED)


class Answer(UUIDPrimaryKeyModel):
    submission = models.ForeignKey(
        Submission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        verbose_name=_("question"),
        on_delete=models.CASCADE,
        related_name="answers",
    )
    option = models.ForeignKey(
        Option,
        verbose_name=_("option"),
        on_delete=models.SET_NULL,
        related_name="answers",
        null=True,
    )
    answered_at = models.DateTimeField(_("answered at"), auto_now_add=True)

    class Meta:
        db_table = "answers"
        verbose_name = _("answer")
        verbose_name_plural = _("answers")
        ordering = ["submission", "question__order"]
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "question"],
                name="unique_submission_question_answer",
            )
        ]

    def __str__(self) -> str:
        return f"{self.submission} → {self.question}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.submission.try_complete()
