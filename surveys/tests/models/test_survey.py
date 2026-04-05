from typing import cast

import pytest
from django.core.exceptions import ValidationError

from surveys.models import Survey
from surveys.tests.factories import SurveyFactory

pytestmark = pytest.mark.django_db


def test_survey_to_str():
    survey = SurveyFactory.build()
    assert str(survey) == survey.title


def test_survey_transition_to_valid():
    survey = cast(Survey, SurveyFactory(status=Survey.StatusChoices.DRAFT))
    survey.transition_to(Survey.StatusChoices.PUBLISHED)
    assert survey.status == Survey.StatusChoices.PUBLISHED


def test_survey_transition_to_invalid():
    survey = cast(Survey, SurveyFactory(status=Survey.StatusChoices.DRAFT))
    with pytest.raises(ValidationError, match="inválida"):
        survey.transition_to(Survey.StatusChoices.CLOSED)
    with pytest.raises(ValidationError, match="inválida"):
        survey.transition_to(Survey.StatusChoices.CLOSED)
        survey.transition_to(Survey.StatusChoices.CLOSED)
