import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_assigned_survey_list(respondent_api_client, granted_accesses):
    url = reverse("surveys:assigned-survey-list")
    response = respondent_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == len(granted_accesses)
    assert len(response.data["results"]) == len(granted_accesses)


def test_assigned_survey_list_unpublished_surveys(
    respondent_api_client, unpublished_surveys
):
    url = reverse("surveys:assigned-survey-list")
    response = respondent_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert len(response.data["results"]) == 0


def test_assigned_survey_list_as_admin(admin_api_client, granted_accesses):
    url = reverse("surveys:assigned-survey-list")
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_assigned_survey_detail(respondent_api_client, respondent_survey):
    url = reverse("surveys:assigned-survey-detail", args=[str(respondent_survey.id)])
    response = respondent_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(respondent_survey.id)
    assert response.data["title"] == respondent_survey.title
    assert "questions" in response.data


def test_assigned_survey_detail_unpublished_survey(
    respondent_api_client, unpublished_surveys
):
    for access in unpublished_surveys:
        url = reverse("surveys:assigned-survey-detail", args=[str(access.survey.id)])
        response = respondent_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


def test_assigned_survey_detail_as_admin(admin_api_client, respondent_survey):
    url = reverse("surveys:assigned-survey-detail", args=[str(respondent_survey.id)])
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_assigned_survey_update(respondent_api_client, respondent_survey):
    url = reverse("surveys:assigned-survey-detail", args=[str(respondent_survey.id)])
    response = respondent_api_client.patch(url, data={"title": "new title"})
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_assigned_survey_delete(respondent_api_client, respondent_survey):
    url = reverse("surveys:assigned-survey-detail", args=[str(respondent_survey.id)])
    response = respondent_api_client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
