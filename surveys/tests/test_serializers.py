import pytest

from surveys.api.serializers import SurveySerializer
from surveys.models import Survey
from surveys.tests.factories import SurveyFactory


@pytest.fixture
def context(request_factory, admin_user):
    request = request_factory.post("/")
    request.user = admin_user
    return {"request": request}


@pytest.mark.django_db
def test_survey_to_serializer(context):
    survey = SurveyFactory()
    serializer = SurveySerializer(instance=survey, context=context)
    assert serializer.data["title"] == survey.title  # type:ignore


@pytest.mark.django_db
def test_serializer_to_survey(context):
    data = {"title": "minha pesquisa", "status": Survey.StatusChoices.DRAFT}
    serializer = SurveySerializer(data=data, context=context)
    assert serializer.is_valid()

    survey = serializer.save()
    assert isinstance(survey, Survey)
    assert survey.title == data["title"]
    assert survey.status == data["status"]


@pytest.mark.django_db
def test_serializer_data_invalid(context):
    data = {"title": None, "status": Survey.StatusChoices.DRAFT}
    serializer = SurveySerializer(data=data, context=context)
    assert not serializer.is_valid()
    assert "title" in serializer.errors
