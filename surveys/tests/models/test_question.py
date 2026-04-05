import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from surveys.models import Question
from surveys.tests.factories import QuestionFactory, SurveyFactory

pytestmark = pytest.mark.django_db


def test_question_to_str():
    question = QuestionFactory.build()
    assert str(question) == question.text


def test_question_unique_survey_order_valid():
    survey = SurveyFactory()
    question1 = QuestionFactory(survey=survey, order=1)
    question2 = QuestionFactory(survey=survey, order=2)

    assert question1.order != question2.order


def test_question_unique_survey_order_invalid():
    survey = SurveyFactory()
    QuestionFactory(survey=survey, order=1)

    with pytest.raises(IntegrityError):
        QuestionFactory(survey=survey, order=1)


def test_question_order_must_be_greater_than_zero():
    survey = SurveyFactory()
    question = QuestionFactory.build(survey=survey, order=0)
    with pytest.raises(ValidationError):
        question.full_clean()


def test_question_ordering_within_survey():
    survey = SurveyFactory()

    question1 = QuestionFactory(survey=survey, order=2)
    question2 = QuestionFactory(survey=survey, order=1)
    question3 = QuestionFactory(survey=survey, order=3)

    questions = list(survey.questions.all())

    assert questions == [question2, question1, question3]


def test_question_order_is_isolated_per_survey():
    survey1 = SurveyFactory(title="A")
    survey2 = SurveyFactory(title="B")

    question1 = QuestionFactory(survey=survey1, order=1)
    question2 = QuestionFactory(survey=survey1, order=2)

    question3 = QuestionFactory(survey=survey2, order=1)

    question_list1 = list(survey1.questions.all())
    question_list2 = list(survey2.questions.all())

    assert question_list1 == [question1, question2]
    assert question_list2 == [question3]


def test_question_auto_increment_order():
    survey = SurveyFactory()

    question1 = Question.objects.create(survey=survey, text="test text")
    question2 = Question.objects.create(survey=survey, text="test text")
    question3 = Question.objects.create(survey=survey, text="test text")

    assert question1.order == 1
    assert question2.order == 2
    assert question3.order == 3
    assert question3.order == 3
