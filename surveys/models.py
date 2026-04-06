import os
import uuid
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from PIL import Image

from core.models import TimeStampedModel, UUIDPrimaryKeyModel
from surveys.utils import get_next_order


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
        _("order"), blank=True, null=True, validators=[MinValueValidator(1)]
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
                next_order = get_next_order(
                    Question, survey=self.survey, select_for_update=True
                )
                self.order = next_order

        super().save(*args, **kwargs)


def question_image_upload_to(instance, filename):
    ext = os.path.splitext(filename)[-1].lower() or ".jpg"
    return f"question_images/{instance.question_id}/{uuid.uuid4()}{ext}"


class QuestionImage(UUIDPrimaryKeyModel):
    question = models.ForeignKey(
        Question,
        verbose_name=_("question"),
        on_delete=models.CASCADE,
        related_name="images",
    )
    file = models.ImageField(_("file"), upload_to=question_image_upload_to)
    order = models.PositiveSmallIntegerField(
        _("order"), blank=True, null=True, validators=[MinValueValidator(1)]
    )
    alt_text = models.CharField(_("alternative text"), max_length=255, blank=True)
    uploaded_at = models.DateTimeField(_("uploaded at"), auto_now_add=True)

    class Meta:
        db_table = "images"
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ["question", "order"]

        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_question_image_order",
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
                next_order = get_next_order(
                    QuestionImage, question=self.question, select_for_update=True
                )
                self.order = next_order

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


class Option(UUIDPrimaryKeyModel):
    question = models.ForeignKey(
        Question,
        verbose_name=_("question"),
        on_delete=models.CASCADE,
        related_name="options",
    )
    text = models.TextField(_("text"))
    order = models.PositiveSmallIntegerField(
        _("order"), blank=True, null=True, validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = "option"
        verbose_name = _("option")
        verbose_name_plural = _("options")
        ordering = ["question", "order"]

        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_question_option_order",
            )
        ]

    def __str__(self) -> str:
        return _('Option {order} for question "{question}": {text}').format(
            order=self.order, question=self.question, text=self.text
        )

    def save(self, *args, **kwargs):
        if self.order is None:
            with transaction.atomic():
                next_order = get_next_order(
                    Option, question=self.question, select_for_update=True
                )
                self.order = next_order

        super().save(*args, **kwargs)
