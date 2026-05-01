from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from apps.answers.models import Submission
from apps.answers.tests.factories import (
    AnswerFactory,
    SubmissionFactory,
)

pytestmark = pytest.mark.django_db


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
    fields = ["id", "submission", "question", "option", "answered_at"]
    for field in fields:
        assert field in response.data


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
