from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from surveys.models import Option, Question, QuestionImage


def reorder_after_delete(model, filter_kwargs, deleted_order):
    with transaction.atomic():
        model.objects.select_for_update().filter(
            **filter_kwargs,
            order__gt=deleted_order,
        ).update(order=models.F("order") - 1)


@receiver(post_delete, sender=Question)
def reorder_questions(sender, instance, **kwargs):
    reorder_after_delete(
        model=Question,
        filter_kwargs={"survey": instance.survey},
        deleted_order=instance.order,
    )


@receiver(post_delete, sender=QuestionImage)
def reorder_question_images(sender, instance, **kwargs):
    reorder_after_delete(
        model=QuestionImage,
        filter_kwargs={"question": instance.question},
        deleted_order=instance.order,
    )


@receiver(post_delete, sender=Option)
def reorder_options(sender, instance, **kwargs):
    reorder_after_delete(
        model=Option,
        filter_kwargs={"question": instance.question},
        deleted_order=instance.order,
    )
