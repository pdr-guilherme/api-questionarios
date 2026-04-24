from typing import cast

import pytest

from apps.answers.models import Answer, Submission
from apps.answers.tests.factories import (
    AnswerFactory,
    SubmissionFactory,
)


@pytest.fixture
def submission(respondent_user):
    return cast(Submission, SubmissionFactory(user=respondent_user))


@pytest.fixture
def answer(submission):
    return cast(Answer, AnswerFactory(submission=submission))
