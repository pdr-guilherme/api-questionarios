import pytest

from surveys.tests.factories import (
    OptionFactory,
    QuestionFactory,
    QuestionImageFactory,
    SurveyFactory,
)

pytestmark = pytest.mark.django_db


def test_reorder_questions_after_delete():
    survey = SurveyFactory()
    question1 = QuestionFactory(survey=survey, auto_order=True)
    question2 = QuestionFactory(survey=survey, auto_order=True)
    question3 = QuestionFactory(survey=survey, auto_order=True)

    question2.delete()
    question1.refresh_from_db()
    question3.refresh_from_db()

    assert question1.order == 1
    assert question3.order == 2


def test_reorder_question_images_after_delete():
    question = QuestionFactory()
    question_image1 = QuestionImageFactory(question=question, auto_order=True)
    question_image2 = QuestionImageFactory(question=question, auto_order=True)
    question_image3 = QuestionImageFactory(question=question, auto_order=True)

    question_image2.delete()
    question_image1.refresh_from_db()
    question_image3.refresh_from_db()

    assert question_image1.order == 1
    assert question_image3.order == 2


def test_reorder_options_after_delete():
    question = QuestionFactory()
    option1 = OptionFactory(question=question, auto_order=True)
    option2 = OptionFactory(question=question, auto_order=True)
    option3 = OptionFactory(question=question, auto_order=True)

    option2.delete()
    option1.refresh_from_db()
    option3.refresh_from_db()

    assert option1.order == 1
    assert option3.order == 2


def test_last_deleted_no_order_change():
    survey = SurveyFactory()
    question1 = QuestionFactory(survey=survey, auto_order=True)
    question2 = QuestionFactory(survey=survey, auto_order=True)

    question2.delete()
    question1.refresh_from_db()

    assert question1.order == 1


def test_reorder_is_independent():
    survey1 = SurveyFactory()
    survey2 = SurveyFactory()
    question1 = QuestionFactory(survey=survey1, auto_order=True)
    question2 = QuestionFactory(survey=survey2, auto_order=True)

    question1.delete()
    question2.refresh_from_db()

    assert question2.order == 1
