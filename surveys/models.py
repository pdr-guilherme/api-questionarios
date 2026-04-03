import os
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
from PIL import Image

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


class QuestionImage(UUIDPrimaryKeyModel):
    question = models.ForeignKey(
        Question,
        verbose_name=_("question"),
        on_delete=models.CASCADE,
        related_name="question_images",
    )
    file = models.ImageField(_("file"), upload_to="question_images/")
    order = models.PositiveSmallIntegerField(
        _("order"), blank=True, validators=[MinValueValidator(1)]
    )
    uploaded_at = models.DateTimeField(_("uploaded at"), auto_now_add=True)

    class Meta:
        db_table = "question_images"
        verbose_name = _("question image")
        verbose_name_plural = _("question images")
        ordering = ["question", "order"]

        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_question_order",
            )
        ]

    def __str__(self) -> str:
        return _("Image for question {question} at order {order}").format(
            question=self.question, order=self.order
        )

    def save(self, *args, **kwargs):
        if self.file:
            self._compress_image()

        if self.order is None:
            with transaction.atomic():
                last_order = (
                    QuestionImage.objects.select_for_update()
                    .filter(question=self.question)
                    .aggregate(Max("order"))["order__max"]
                )
                self.order = (last_order or 0) + 1

        super().save(*args, **kwargs)

    def _compress_image(self):
        img = Image.open(self.file)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        buffer.seek(0)

        filename = os.path.splitext(self.file.name)[0] + ".jpg"
        self.file.save(filename, ContentFile(buffer.read()), save=False)
