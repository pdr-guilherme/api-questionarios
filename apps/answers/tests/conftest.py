from typing import cast

import pytest

from apps.answers.models import Answer, Submission, SurveyAccess
from apps.answers.tests.factories import (
    AnswerFactory,
    SubmissionFactory,
    SurveyAccessFactory,
)
from apps.surveys.models import Survey
from apps.surveys.tests.factories import SurveyFactory


@pytest.fixture
def respondent_context(request_factory, respondent_user):
    request = request_factory.post("/")
    request.user = respondent_user
    return {"request": request}


@pytest.fixture
def survey_access(respondent_user):
    return cast(SurveyAccess, SurveyAccessFactory(user=respondent_user))


@pytest.fixture
def submission(respondent_user, survey_access):
    return cast(
        Submission, SubmissionFactory(user=respondent_user, survey=survey_access.survey)
    )


@pytest.fixture
def answer(submission):
    return cast(Answer, AnswerFactory(submission=submission))


@pytest.fixture
def published_survey_access(respondent_user):
    survey = SurveyFactory(status=Survey.StatusChoices.PUBLISHED)
    return cast(SurveyAccess, SurveyAccessFactory(survey=survey, user=respondent_user))
