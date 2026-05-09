import pytest

from apps.surveys.api.serializers import SurveySerializer
from apps.surveys.models import Survey
from apps.surveys.tests.factories import SurveyFactory

pytestmark = pytest.mark.django_db


def test_survey_to_serializer(admin_context):
    survey = SurveyFactory()
    serializer = SurveySerializer(instance=survey, context=admin_context)
    assert serializer.data["title"] == survey.title  # type: ignore


def test_serializer_to_survey(admin_context):
    data = {"title": "minha pesquisa", "status": Survey.StatusChoices.DRAFT}
    serializer = SurveySerializer(data=data, context=admin_context)
    assert serializer.is_valid(), serializer.errors

    survey = serializer.save()
    assert isinstance(survey, Survey)
    assert survey.title == data["title"]
    assert survey.status == data["status"]


def test_survey_serializer_data_invalid(admin_context):
    data = {"title": None, "status": Survey.StatusChoices.DRAFT}
    serializer = SurveySerializer(data=data, context=admin_context)
    assert not serializer.is_valid(), serializer.errors
    assert "title" in serializer.errors
