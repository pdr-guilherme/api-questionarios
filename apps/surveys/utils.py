from typing import TYPE_CHECKING, Optional

from django.db.models import Max

if TYPE_CHECKING:
    from apps.surveys.models import Option, Question, QuestionImage, Survey


def get_next_order(
    model: "type[Question | QuestionImage | Option]",
    survey: "Optional[Survey]" = None,
    question: "Optional[Question]" = None,
    select_for_update: bool = False,
) -> int:
    from apps.surveys.models import Question

    if issubclass(model, Question):
        if survey is None:
            raise TypeError("A valid value for survey must be passed")
        filter_kwargs = {"survey": survey}
    else:
        if question is None:
            raise TypeError("A valid value for question must be passed")
        filter_kwargs = {"question": question}

    qs = model.objects.filter(**filter_kwargs)
    if select_for_update:
        qs = qs.select_for_update()

    last_order = qs.aggregate(Max("order"))["order__max"]
    return (last_order or 0) + 1
