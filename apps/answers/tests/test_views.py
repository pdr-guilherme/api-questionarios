from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from apps.answers.models import Submission
from apps.answers.tests.factories import (
    AnswerFactory,
    SubmissionFactory,
    SurveyAccessFactory,
)

pytestmark = pytest.mark.django_db


def test_submission_create(respondent_api_client, respondent_user):
    survey_access = SurveyAccessFactory(user=respondent_user)
    data = {"survey": str(survey_access.survey.id)}
    url = reverse("answers:submission-list")
    response = respondent_api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Submission.objects.count() == 1


def test_submission_create_read_only_fields(respondent_api_client, respondent_user):
    survey_access = SurveyAccessFactory(user=respondent_user)
    url = reverse("answers:submission-list")
    fake_date = "2000-01-01T00:00:00Z"
    data = {
        "survey": str(survey_access.survey.id),
        "id": "90dc1281-cbd9-4168-ba46-5e56434056c3",
        "started_at": fake_date,
        "finished_at": fake_date,
        "status": Submission.StatusChoices.COMPLETED,
    }
    response = respondent_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["id"] != data["id"]
    assert response.data["started_at"] != data["started_at"]
    assert response.data["finished_at"] is None
    assert response.data["status"] == Submission.StatusChoices.DRAFT


def test_submission_list(respondent_api_client, respondent_user):
    SubmissionFactory.create_batch(5, user=respondent_user)
    url = reverse("answers:submission-list")
    response = respondent_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 5
    assert len(response.data["results"]) == 5


def test_submission_detail(respondent_api_client, submission):
    url = reverse("answers:submission-detail", kwargs={"pk": str(submission.id)})
    response = respondent_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == Submission.StatusChoices.DRAFT
    assert "answers" in response.data
    assert "created_at" in response.data
    assert "updated_at" in response.data


def test_submission_update(respondent_api_client, submission):
    url = reverse("answers:submission-detail", kwargs={"pk": str(submission.id)})
    response = respondent_api_client.put(url, data={}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_submission_partial_update(respondent_api_client, submission):
    url = reverse("answers:submission-detail", kwargs={"pk": str(submission.id)})
    response = respondent_api_client.patch(url, data={}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_submission_delete_completed_submission(respondent_api_client, submission):
    submission.status = Submission.StatusChoices.COMPLETED
    submission.save()

    url = reverse("answers:submission-detail", kwargs={"pk": str(submission.id)})
    response = respondent_api_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_submission_delete_draft_submission(respondent_api_client, submission):
    url = reverse("answers:submission-detail", kwargs={"pk": str(submission.id)})
    response = respondent_api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_answer_create(respondent_api_client, published_survey_access, respondent_user):
    answer_data = AnswerFactory(survey=published_survey_access.survey)
    submission = SubmissionFactory(
        user=respondent_user, survey=published_survey_access.survey
    )
    data = {
        "submission": str(submission.id),
        "question": str(answer_data.question.id),
        "option": str(answer_data.option.id),
    }
    url = reverse("answers:answer-list", kwargs={"submission_pk": str(submission.id)})
    response = respondent_api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


def test_answer_list(respondent_api_client, respondent_user, published_survey_access):
    submission = SubmissionFactory(
        user=respondent_user, survey=published_survey_access.survey
    )
    with patch.object(Submission, "try_complete", return_value=None):
        AnswerFactory.create_batch(5, submission=submission)

    url = reverse("answers:answer-list", kwargs={"submission_pk": str(submission.id)})
    response = respondent_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_answer_detail(respondent_api_client, submission, answer):
    url = reverse(
        "answers:answer-detail",
        kwargs={"submission_pk": str(submission.id), "pk": str(answer.id)},
    )
    response = respondent_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.data
    assert "submission" in response.data
    assert "question" in response.data
    assert "option" in response.data
    assert "answered_at" in response.data


def test_answer_update(respondent_api_client, submission, answer):
    url = reverse(
        "answers:answer-detail",
        kwargs={"submission_pk": str(submission.id), "pk": str(answer.id)},
    )
    response = respondent_api_client.put(url, data={}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_answer_partial_update(respondent_api_client, submission, answer):
    url = reverse(
        "answers:answer-detail",
        kwargs={"submission_pk": str(submission.id), "pk": str(answer.id)},
    )
    response = respondent_api_client.patch(url, data={}, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_answer_delete_draft_submission(respondent_api_client, submission, answer):
    submission.status = Submission.StatusChoices.DRAFT
    submission.save()

    url = reverse(
        "answers:answer-detail",
        kwargs={"submission_pk": str(submission.id), "pk": str(answer.id)},
    )
    response = respondent_api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_answer_delete_completed_submission(respondent_api_client, submission, answer):
    submission.status = Submission.StatusChoices.COMPLETED
    submission.save()

    url = reverse(
        "answers:answer-detail",
        kwargs={"submission_pk": str(submission.id), "pk": str(answer.id)},
    )
    response = respondent_api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    submission.refresh_from_db()
    assert submission.status == submission.StatusChoices.DRAFT
