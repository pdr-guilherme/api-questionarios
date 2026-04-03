from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, UUIDPrimaryKeyModel


class Survey(UUIDPrimaryKeyModel, TimeStampedModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", _("rascunho")
        PUBLISHED = "published", _("publicado")
        CLOSED = "closed", _("encerrado")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="surveys",
    )
    title = models.CharField(_("title"), max_length=255)
    status = models.CharField(
        _("status"),
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )

    VALID_TRANSITIONS: dict[StatusChoices, list[StatusChoices]] = {
        StatusChoices.DRAFT: [StatusChoices.PUBLISHED],
        StatusChoices.PUBLISHED: [StatusChoices.CLOSED],
        StatusChoices.CLOSED: [],
    }

    def transition_to(self, new_status: StatusChoices):
        allowed = self.VALID_TRANSITIONS.get(self.status, [])  # type:ignore
        if new_status not in allowed:
            raise ValidationError(f"Transição inválida: {self.status} → {new_status}")
        self.status = new_status
        self.save()

    class Meta:
        db_table = "surveys"
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")
        ordering = ["title", "-updated_at"]

    def __str__(self) -> str:
        return self.title


class Question(UUIDPrimaryKeyModel, TimeStampedModel):
    survey = models.ForeignKey(
        Survey,
        verbose_name=_("survey"),
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.CharField(_("question text"), max_length=255)
    order = models.PositiveSmallIntegerField(
        _("order"), validators=[MinValueValidator(1)]
    )
    is_required = models.BooleanField(_("is required"), default=True)

    class Meta:
        db_table = "questions"
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ["survey__title", "order"]

        constraints = [
            models.UniqueConstraint(
                fields=["survey", "order"],
                name="unique_survey_order",
            )
        ]

    def __str__(self) -> str:
        return self.text

    def save(self, *args, **kwargs):
        if self.order is None:
            with transaction.atomic():
                last_order = (
                    Question.objects.select_for_update()
                    .filter(survey=self.survey)
                    .aggregate(Max("order"))["order__max"]
                )
                self.order = (last_order or 0) + 1

        super().save(*args, **kwargs)
