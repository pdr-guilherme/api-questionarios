from typing import cast

import pytest

from apps.answers.models import SurveyAccess
from apps.answers.tests.factories import SurveyAccessFactory
from apps.surveys.models import Option, Question, QuestionImage, Survey
from apps.surveys.tests.factories import (
    OptionFactory,
    QuestionFactory,
    QuestionImageFactory,
    SurveyFactory,
)


@pytest.fixture
def survey(admin_user):
    return cast(Survey, SurveyFactory(author=admin_user))


@pytest.fixture
def granted_accesses(respondent_user):
    return cast(
        list[SurveyAccess],
        SurveyAccessFactory.create_batch(
            3, user=respondent_user, survey__status=Survey.StatusChoices.PUBLISHED
        ),
    )


@pytest.fixture
def unpublished_surveys(respondent_user):
    surveys = [
        SurveyAccessFactory(
            user=respondent_user, survey__status=Survey.StatusChoices.DRAFT
        ),
        SurveyAccessFactory(
            user=respondent_user, survey__status=Survey.StatusChoices.CLOSED
        ),
    ]
    return cast(list[SurveyAccess], surveys)


@pytest.fixture
def respondent_survey(granted_accesses):
    survey = granted_accesses[0].survey
    return survey


@pytest.fixture
def question(survey):
    return cast(Question, QuestionFactory(survey=survey))


@pytest.fixture
def option(question):
    return cast(Option, OptionFactory(question=question, auto_order=True))


@pytest.fixture
def question_image(question):
    return cast(
        QuestionImage, QuestionImageFactory.create(auto_order=True, question=question)
    )
