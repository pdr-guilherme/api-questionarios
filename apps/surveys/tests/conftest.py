from typing import cast

import pytest

from apps.surveys.models import Option, Question, QuestionImage, Survey
from apps.surveys.tests.factories import (
    OptionFactory,
    QuestionFactory,
    QuestionImageFactory,
    SurveyFactory,
)


@pytest.fixture
def context(request_factory, admin_user):
    request = request_factory.post("/")
    request.user = admin_user
    return {"request": request}


@pytest.fixture
def survey(admin_user):
    return cast(Survey, SurveyFactory(author=admin_user))


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
