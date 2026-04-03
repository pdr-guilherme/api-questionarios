from typing import cast

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from surveys.models import Question, Survey
from surveys.tests.factories import QuestionFactory, SurveyFactory


@pytest.mark.django_db
def test_survey_to_str():
    survey = SurveyFactory.build()
    assert str(survey) == survey.title


@pytest.mark.django_db
def test_survey_transition_to_valid():
    survey = cast(Survey, SurveyFactory(status=Survey.StatusChoices.DRAFT))
    survey.transition_to(Survey.StatusChoices.PUBLISHED)
    assert survey.status == Survey.StatusChoices.PUBLISHED


@pytest.mark.django_db
def test_survey_transition_to_invalid():
    survey = cast(Survey, SurveyFactory(status=Survey.StatusChoices.DRAFT))
    with pytest.raises(ValidationError, match="inválida"):
        survey.transition_to(Survey.StatusChoices.CLOSED)


@pytest.mark.django_db
def test_question_to_str():
    question = QuestionFactory.build()
    assert str(question) == question.text


@pytest.mark.django_db
def test_question_unique_survey_order_valid():
    survey = SurveyFactory()
    question1 = QuestionFactory(survey=survey, order=1)
    question2 = QuestionFactory(survey=survey, order=2)

    assert question1.order != question2.order


@pytest.mark.django_db
def test_question_unique_survey_order_invalid():
    survey = SurveyFactory()
    QuestionFactory(survey=survey, order=1)

    with pytest.raises(IntegrityError):
        QuestionFactory(survey=survey, order=1)


@pytest.mark.django_db
def test_question_order_must_be_greater_than_zero():
    survey = SurveyFactory()
    question = QuestionFactory.build(survey=survey, order=0)
    with pytest.raises(ValidationError):
        question.full_clean()


@pytest.mark.django_db
def test_question_ordering_within_survey():
    survey = SurveyFactory()

    q1 = QuestionFactory(survey=survey, order=2)
    q2 = QuestionFactory(survey=survey, order=1)
    q3 = QuestionFactory(survey=survey, order=3)

    questions = list(survey.questions.all())

    assert questions == [q2, q1, q3]


@pytest.mark.django_db
def test_question_order_is_isolated_per_survey():
    s1 = SurveyFactory(title="A")
    s2 = SurveyFactory(title="B")

    q1 = QuestionFactory(survey=s1, order=1)
    q2 = QuestionFactory(survey=s1, order=2)

    q3 = QuestionFactory(survey=s2, order=1)

    qs1 = list(s1.questions.all())
    qs2 = list(s2.questions.all())

    assert qs1 == [q1, q2]
    assert qs2 == [q3]


@pytest.mark.django_db
def test_auto_increment_order():
    survey = SurveyFactory()

    q1 = Question.objects.create(survey=survey, text="test text")
    q2 = Question.objects.create(survey=survey, text="test text")
    q3 = Question.objects.create(survey=survey, text="test text")

    assert q1.order == 1
    assert q2.order == 2
    assert q3.order == 3
