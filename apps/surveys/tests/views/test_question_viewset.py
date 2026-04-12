from typing import cast

import pytest
from django.urls import reverse
from rest_framework import status

from apps.surveys.models import Question, Survey
from apps.surveys.tests.factories import QuestionFactory, SurveyFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def survey(admin_user):
    return cast(Survey, SurveyFactory(author=admin_user))


def test_question_create(api_client, admin_user, survey):
    data = {"text": "test text", "survey": str(survey.id)}
    url = reverse("surveys:question-list")
    api_client.force_authenticate(admin_user)
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["text"] == data["text"]
    assert response.data["is_required"]
    assert response.data["order"] == 1


def test_question_create_invalid_data(api_client, admin_user, survey):
    data = {"text": "", "survey": str(survey.id)}
    url = reverse("surveys:question-list")
    api_client.force_authenticate(admin_user)
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_question_list(api_client, admin_user, survey):
    QuestionFactory.create_batch(5, survey=survey)
    url = reverse("surveys:question-list")
    api_client.force_authenticate(admin_user)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 5
    assert len(response.data["results"]) == 5


def test_question_detail(api_client, admin_user, survey):
    question = QuestionFactory.create(survey=survey)
    url = reverse("surveys:question-detail", kwargs={"pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["text"] == question.text
    assert response.data["is_required"] == question.is_required
    assert response.data["order"] == question.order


def test_question_update(api_client, admin_user, survey):
    data = {
        "text": "test text",
        "order": 2,
        "is_required": False,
        "survey": str(survey.id),
    }
    question = QuestionFactory.create(survey=survey)
    url = reverse("surveys:question-detail", kwargs={"pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["text"] == data["text"]
    assert response.data["is_required"] == data["is_required"]
    assert response.data["order"] == data["order"]


def test_question_partial_update(api_client, admin_user, survey):
    data = {"is_required": False}
    question = QuestionFactory.create(survey=survey, is_required=True)
    url = reverse("surveys:question-detail", kwargs={"pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["text"] == question.text
    assert response.data["is_required"] == data["is_required"]
    assert response.data["order"] == question.order


def test_question_delete(api_client, admin_user, survey):
    question = QuestionFactory.create(survey=survey)
    url = reverse("surveys:question-detail", kwargs={"pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Question.objects.filter(pk=question.id).exists()
