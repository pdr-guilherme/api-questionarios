from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
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
