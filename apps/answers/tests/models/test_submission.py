import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.answers.models import Submission
from apps.answers.tests.factories import AnswerFactory, SubmissionFactory
from apps.surveys.tests.factories import QuestionFactory

pytestmark = pytest.mark.django_db


def test_submission_to_str(submission):
    assert (
        str(submission)
        == f"{submission.user} → {submission.survey} ({submission.status})"
    )


def test_submission_unique_user_survey(submission):
    with pytest.raises(IntegrityError):
        SubmissionFactory.create(survey=submission.survey, user=submission.user)


def test_submission_different_surveys(respondent_user):
    sub1 = SubmissionFactory(user=respondent_user)
    sub2 = SubmissionFactory(user=respondent_user)
    assert sub1.user == sub2.user


def test_submission_started_at(submission):
    assert submission.started_at is not None


def test_submission_finished_at_is_empty(submission):
    assert submission.finished_at is None


def test_submission_transition_to_valid(submission):
    submission.transition_to(Submission.StatusChoices.COMPLETED)
    assert submission.status == Submission.StatusChoices.COMPLETED


def test_submission_transition_to_invalid():
    submission = SubmissionFactory(status=Submission.StatusChoices.COMPLETED)
    with pytest.raises(ValidationError, match="inválida"):
        submission.transition_to(Submission.StatusChoices.DRAFT)


def test_submission_try_complete_valid(submission):
    question1, question2 = QuestionFactory.create_batch(
        2, survey=submission.survey, is_required=True, auto_order=True
    )
    # responde as duas
    AnswerFactory(submission=submission, question=question1)
    AnswerFactory(submission=submission, question=question2)
    submission.status = Submission.StatusChoices.DRAFT

    submission.try_complete()
    submission.refresh_from_db()

    assert submission.status == Submission.StatusChoices.COMPLETED
    assert submission.finished_at is not None


def test_submission_try_complete_invalid(submission):
    question1, _question2 = QuestionFactory.create_batch(
        2, survey=submission.survey, is_required=True, auto_order=True
    )

    # responde apenas a primeira
    AnswerFactory(submission=submission, question=question1)

    submission.try_complete()
    submission.refresh_from_db()

    assert submission.status == Submission.StatusChoices.DRAFT
    assert submission.finished_at is None
