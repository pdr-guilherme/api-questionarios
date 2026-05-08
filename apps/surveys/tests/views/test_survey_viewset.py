import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from apps.answers.models import SurveyAccess
from apps.surveys.models import Survey
from apps.surveys.tests.factories import SurveyFactory

pytestmark = pytest.mark.django_db


def test_survey_create(admin_api_client):
    data = {"title": "my survey", "status": "draft"}
    url = reverse("surveys:survey-list")

    response = admin_api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == data["title"]
    assert response.data["status"] == data["status"]


def test_survey_create_non_admin(api_client, respondent_user):
    url = reverse("surveys:survey-list")
    api_client.force_authenticate(respondent_user)

    response = api_client.post(url, data={}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_list(admin_api_client, admin_user):
    SurveyFactory.create_batch(5, author=admin_user)
    url = reverse("surveys:survey-list")

    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 5
    assert len(response.data["results"]) == 5


def test_survey_list_non_admin(api_client, respondent_user):
    url = reverse("surveys:survey-list")
    api_client.force_authenticate(respondent_user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_detail(admin_api_client, survey):
    url = reverse("surveys:survey-detail", kwargs={"pk": str(survey.id)})

    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == survey.title
    assert response.data["status"] == survey.status
    assert "questions" in response.data
    assert "respondents" in response.data


def test_survey_detail_non_admin(api_client, respondent_user):
    url = reverse("surveys:survey-detail", kwargs={"pk": str(uuid.uuid4())})
    api_client.force_authenticate(respondent_user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_update(admin_api_client, survey):
    data = {"title": "new title", "status": "published"}
    url = reverse("surveys:survey-detail", kwargs={"pk": str(survey.id)})

    response = admin_api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == data["title"]
    assert response.data["status"] == data["status"]


def test_survey_update_non_admin(api_client, respondent_user):
    url = reverse("surveys:survey-detail", kwargs={"pk": str(uuid.uuid4())})
    api_client.force_authenticate(respondent_user)

    response = api_client.put(url, data={}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_partial_update(admin_api_client, survey):
    data = {"status": "published"}
    url = reverse("surveys:survey-detail", kwargs={"pk": str(survey.id)})

    response = admin_api_client.patch(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == survey.title
    assert response.data["status"] == data["status"]


def test_survey_partial_update_non_admin(api_client, respondent_user):
    url = reverse("surveys:survey-detail", kwargs={"pk": str(uuid.uuid4())})
    api_client.force_authenticate(respondent_user)

    response = api_client.patch(url, data={}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_delete(admin_api_client, survey):
    url = reverse("surveys:survey-detail", kwargs={"pk": str(survey.id)})

    response = admin_api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_survey_delete_non_admin(api_client, respondent_user):
    url = reverse("surveys:survey-detail", kwargs={"pk": str(uuid.uuid4())})
    api_client.force_authenticate(respondent_user)

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_publish(admin_api_client, survey):
    url = reverse("surveys:survey-publish", kwargs={"pk": str(survey.id)})

    response = admin_api_client.post(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    survey.refresh_from_db()
    assert survey.status == Survey.StatusChoices.PUBLISHED


def test_survey_publish_from_invalid_status(admin_api_client, admin_user):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.CLOSED)
    url = reverse("surveys:survey-publish", kwargs={"pk": str(survey.id)})

    response = admin_api_client.post(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_survey_close(admin_api_client, admin_user):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.PUBLISHED)
    url = reverse("surveys:survey-close", kwargs={"pk": str(survey.id)})

    response = admin_api_client.post(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    survey.refresh_from_db()
    assert survey.status == Survey.StatusChoices.CLOSED


def test_survey_close_from_invalid_status(admin_api_client, admin_user):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.DRAFT)
    url = reverse("surveys:survey-close", kwargs={"pk": str(survey.id)})

    response = admin_api_client.post(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_survey_grant_user_access(admin_api_client, admin_user, respondent_user):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.PUBLISHED)
    data = {"user_id": str(respondent_user.id)}
    url = reverse("surveys:survey-grant-access", kwargs={"pk": str(survey.id)})

    response = admin_api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_survey_revoke_user_access(admin_api_client, admin_user, respondent_user):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.PUBLISHED)
    data = {"user_id": str(respondent_user.id)}
    url = reverse("surveys:survey-revoke-access", kwargs={"pk": str(survey.id)})

    response = admin_api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_survey_grant_user_access_is_idempotent(
    admin_api_client, admin_user, respondent_user
):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.PUBLISHED)
    data = {"user_id": str(respondent_user.id)}
    url = reverse("surveys:survey-grant-access", kwargs={"pk": str(survey.id)})

    admin_api_client.post(url, data=data, format="json")  # primeira vez
    response = admin_api_client.post(url, data=data, format="json")  # segunda vez
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert SurveyAccess.objects.filter(survey=survey, user=respondent_user).count() == 1


def test_survey_revoke_user_access_is_idempotent(
    admin_api_client, admin_user, respondent_user
):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.PUBLISHED)
    data = {"user_id": str(respondent_user.id)}
    url = reverse("surveys:survey-revoke-access", kwargs={"pk": str(survey.id)})

    admin_api_client.post(url, data=data, format="json")  # primeira vez
    response = admin_api_client.post(url, data=data, format="json")  # segunda vez
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert (
        SurveyAccess.objects.filter(survey=survey, user=respondent_user).exists()
        is False
    )


@pytest.mark.parametrize(
    "data",
    [{"user_id": ""}, {"user_id": "99ff2dcb-f7d0-417a-a8ae-c617f52a7ebe"}, {}],
    ids=["empty user id", "non-existent user", "empty payload"],
)
def test_survey_grant_user_access_invalid_user(admin_api_client, admin_user, data):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.PUBLISHED)
    url = reverse("surveys:survey-grant-access", kwargs={"pk": str(survey.id)})

    response = admin_api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "data",
    [{"user_id": ""}, {"user_id": "99ff2dcb-f7d0-417a-a8ae-c617f52a7ebe"}, {}],
    ids=["empty user id", "non-existent user", "empty payload"],
)
def test_survey_revoke_user_access_invalid_user(admin_api_client, admin_user, data):
    survey = SurveyFactory(author=admin_user, status=Survey.StatusChoices.PUBLISHED)
    url = reverse("surveys:survey-revoke-access", kwargs={"pk": str(survey.id)})

    response = admin_api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
