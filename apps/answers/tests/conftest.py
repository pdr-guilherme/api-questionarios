from typing import cast

import pytest

from apps.answers.models import Answer, Submission, SurveyAccess
from apps.answers.tests.factories import (
    AnswerFactory,
    SubmissionFactory,
    SurveyAccessFactory,
)


@pytest.fixture
def respondent_context(request_factory, respondent_user):
    request = request_factory.post("/")
    request.user = respondent_user
    return {"request": request}


@pytest.fixture
def survey_access(respondent_user):
    return cast(SurveyAccess, SurveyAccessFactory.create(user=respondent_user))


@pytest.fixture
def submission(respondent_user):
    return cast(Submission, SubmissionFactory(user=respondent_user))


@pytest.fixture
def answer(submission):
    return cast(Answer, AnswerFactory(submission=submission))
