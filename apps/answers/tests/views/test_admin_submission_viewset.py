from typing import cast

import pytest
from django.urls import reverse
from rest_framework import status

from apps.answers.models import Submission
from apps.answers.tests.factories import SubmissionFactory, SurveyAccessFactory
from apps.surveys.models import Survey
from apps.surveys.tests.factories import SurveyFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def other_admin_submission():
    other_survey = SurveyFactory(status=Survey.StatusChoices.PUBLISHED)
    other_access = SurveyAccessFactory(survey=other_survey)
    return cast(
        Submission,
        SubmissionFactory(
            user=other_access.user,
            survey=other_survey,
        ),
    )


def test_admin_submission_list(admin_api_client, admin_submissions):
    url = reverse("answers:admin:admin-submission-list")
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == len(admin_submissions)
    assert len(response.data["results"]) == len(admin_submissions)


def test_admin_submission_detail(admin_api_client, admin_submissions):
    admin_submission = admin_submissions[0]
    url = reverse(
        "answers:admin:admin-submission-detail", kwargs={"pk": str(admin_submission.id)}
    )
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    fields = [
        "id",
        "user_email",
        "survey_title",
        "status",
        "started_at",
        "finished_at",
        "answers_count",
        "answers",
    ]
    for field in fields:
        assert field in response.data


def test_admin_submission_list_isolated_submissions(
    admin_api_client, admin_submissions, other_admin_submission
):
    url = reverse("answers:admin:admin-submission-list")
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    returned_ids = {item["id"] for item in response.data["results"]}
    expected_ids = {str(submission.id) for submission in admin_submissions}

    assert expected_ids.issubset(returned_ids)
    assert str(other_admin_submission.id) not in returned_ids


def test_admin_submission_detail_access_other_submission(
    admin_api_client, other_admin_submission
):
    url = reverse(
        "answers:admin:admin-submission-detail",
        kwargs={"pk": str(other_admin_submission.id)},
    )
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_submission_list_as_respondent(respondent_api_client, admin_submissions):
    url = reverse("answers:admin:admin-submission-list")
    response = respondent_api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_submission_detail_as_respondent(
    respondent_api_client, admin_submissions
):
    admin_submission = admin_submissions[0]
    url = reverse(
        "answers:admin:admin-submission-detail", kwargs={"pk": str(admin_submission.id)}
    )
    response = respondent_api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
