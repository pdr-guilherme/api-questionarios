import pytest
from django.db import IntegrityError

from apps.answers.models import SurveyAccess
from apps.answers.tests.factories import SurveyAccessFactory
from apps.surveys.tests.factories import SurveyFactory
from apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_survey_access_to_str(survey_access):
    assert str(survey_access.user) in str(survey_access)
    assert str(survey_access.survey) in str(survey_access)


def test_survey_access_unique_survey_user(survey_access):
    with pytest.raises(IntegrityError):
        SurveyAccessFactory.create(survey=survey_access.survey, user=survey_access.user)


def test_survey_access_granted_at(survey_access):
    assert survey_access.granted_at is not None


def test_survey_access_survey_delete_cascade():
    survey = SurveyFactory()
    survey_access = SurveyAccessFactory(survey=survey)
    assert survey_access.survey == survey

    survey.delete()
    assert SurveyAccess.objects.count() == 0


def test_survey_access_user_delete_cascade():
    user = UserFactory()
    survey_access = SurveyAccessFactory(user=user)
    assert survey_access.user == user

    user.delete()
    assert SurveyAccess.objects.count() == 0


def test_survey_access_respondents():
    survey = SurveyFactory()
    SurveyAccessFactory.create_batch(5, survey=survey)
    assert survey.respondents.exists()
    assert survey.respondents.count() == 5


def test_user_access_survey():
    user = UserFactory()
    SurveyAccessFactory.create_batch(3, user=user)
    assert user.accessible_surveys.exists()
    assert user.accessible_surveys.count() == 3
