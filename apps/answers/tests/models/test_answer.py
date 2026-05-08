import pytest
from django.db import IntegrityError

from apps.answers.tests.factories import AnswerFactory

pytestmark = pytest.mark.django_db


def test_answer_to_str(answer):
    assert str(answer) == f"{answer.submission} → {answer.question}"


def test_answer_unique_submission_question(answer):
    with pytest.raises(IntegrityError):
        AnswerFactory(submission=answer.submission, question=answer.question)


def test_answer_answered_at(answer):
    assert answer.answered_at is not None
