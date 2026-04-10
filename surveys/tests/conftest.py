from typing import cast

import pytest

from surveys.models import Question
from surveys.tests.factories import QuestionFactory


@pytest.fixture
def context(request_factory, admin_user):
    request = request_factory.post("/")
    request.user = admin_user
    return {"request": request}


@pytest.fixture
def question(admin_user):
    return cast(Question, QuestionFactory(survey__author=admin_user))
