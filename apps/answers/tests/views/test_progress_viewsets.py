import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_survey_progress_list(admin_api_client, admin_survey):
    url = reverse("answers:progress:progress-survey-list")
    response = admin_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


def test_survey_progress_detail(admin_api_client, admin_survey):
    url = reverse(
        "answers:progress:progress-survey-detail", kwargs={"pk": str(admin_survey.id)}
    )
    response = admin_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    fields = [
        "id",
        "title",
        "status",
        "total_respondents",
        "not_started",
        "in_progress",
        "completed",
        "completion_rate",
        "created_at",
        "updated_at",
    ]

    for field in fields:
        assert field in response.data


def test_respondent_progress_list(admin_api_client, admin_survey, admin_accesses):
    url = reverse(
        "answers:progress:progress-respondent-list",
        kwargs={"survey_pk": str(admin_survey.pk)},
    )
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3
    assert len(response.data["results"]) == 3


def test_respondent_progress_detail(admin_api_client, admin_survey, admin_accesses):
    survey_access = admin_accesses[0]
    url = reverse(
        "answers:progress:progress-respondent-detail",
        kwargs={"survey_pk": str(admin_survey.pk), "pk": str(survey_access.pk)},
    )
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    fields = [
        "id",
        "user_id",
        "email",
        "status",
        "progress_percentage",
        "unanswered_required_count",
        "started_at",
        "finished_at",
        "questions",
    ]
    for field in fields:
        assert field in response.data

    assert isinstance(response.data["questions"], list)
