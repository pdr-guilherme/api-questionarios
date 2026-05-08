import pytest
from django.urls import reverse
from rest_framework import status

from apps.surveys.models import Option
from apps.surveys.tests.factories import OptionFactory

pytestmark = pytest.mark.django_db


def test_option_create(admin_api_client, question):
    url = reverse("surveys:option-list", kwargs={"question_pk": str(question.id)})
    response = admin_api_client.post(url, data={"text": "test option"}, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["text"] == "test option"
    assert response.data["order"] == 1
    assert response.data["question"] == question.id


def test_option_create_invalid_data(admin_api_client, question):
    url = reverse("surveys:option-list", kwargs={"question_pk": str(question.id)})
    response = admin_api_client.post(url, data={"text": ""}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_option_list(admin_api_client, question):
    OptionFactory.create_batch(5, auto_order=True, question=question)
    url = reverse("surveys:option-list", kwargs={"question_pk": str(question.id)})
    response = admin_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 5
    assert len(response.data["results"]) == 5


def test_option_detail(admin_api_client, question, option):
    url = reverse(
        "surveys:option-detail",
        kwargs={"question_pk": str(question.id), "pk": str(option.id)},
    )
    response = admin_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(option.id)


def test_option_update(admin_api_client, question, option):
    data = {"question": str(question.id), "text": "new text", "order": 2}
    url = reverse(
        "surveys:option-detail",
        kwargs={"question_pk": str(question.id), "pk": str(option.id)},
    )
    response = admin_api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(option.id)
    assert response.data["text"] == data["text"]
    assert response.data["order"] == data["order"]


def test_option_partial_update(admin_api_client, question, option):
    url = reverse(
        "surveys:option-detail",
        kwargs={"question_pk": str(question.id), "pk": str(option.id)},
    )
    response = admin_api_client.patch(url, data={"text": "new text"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(option.id)
    assert response.data["text"] == "new text"
    assert response.data["order"] == option.order


def test_option_delete(admin_api_client, question, option):
    url = reverse(
        "surveys:option-detail",
        kwargs={"question_pk": str(question.id), "pk": str(option.id)},
    )
    response = admin_api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Option.objects.filter(id=option.id).exists()
