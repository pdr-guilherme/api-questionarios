import pytest
from django.db import IntegrityError

from apps.answers.models import Submission
from apps.answers.tests.factories import AnswerFactory
from apps.surveys.tests.factories import QuestionFactory

pytestmark = pytest.mark.django_db


def test_answer_to_str(answer):
    assert str(answer) == f"{answer.submission} → {answer.question}"


def test_answer_unique_submission_question(answer):
    with pytest.raises(IntegrityError):
        AnswerFactory(submission=answer.submission, question=answer.question)


def test_answer_answered_at(answer):
    assert answer.answered_at is not None


def test_answer_save_set_submission_as_complete(submission):
    question1, question2 = QuestionFactory.create_batch(
        2, survey=submission.survey, is_required=True, auto_order=True
    )
    # primeira resposta > ainda draft
    AnswerFactory(submission=submission, question=question1)
    submission.refresh_from_db()
    assert submission.status == Submission.StatusChoices.DRAFT

    # segunda resposta > save chama try_complete > efeito colateral do status
    AnswerFactory(submission=submission, question=question2)
    submission.refresh_from_db()

    assert submission.status == Submission.StatusChoices.COMPLETED
    assert submission.finished_at is not None


def test_answer_delete_revert_submission_status(submission):
    question1, question2 = QuestionFactory.create_batch(
        2, survey=submission.survey, is_required=True, auto_order=True
    )
    # primeira resposta > ainda draft
    AnswerFactory(submission=submission, question=question1)
    submission.refresh_from_db()
    assert submission.status == Submission.StatusChoices.DRAFT

    # segunda resposta > delete chama try_revert > efeito colateral do status
    answer = AnswerFactory(submission=submission, question=question2)
    answer.delete()
    submission.refresh_from_db()

    assert submission.status == Submission.StatusChoices.DRAFT
    assert submission.finished_at is None
