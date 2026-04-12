import pytest
from django.urls import reverse
from rest_framework import status

from apps.surveys.models import Option
from apps.surveys.tests.factories import OptionFactory

pytestmark = pytest.mark.django_db


def test_option_create(api_client, admin_user, question):
    url = reverse("surveys:option-list", kwargs={"question_pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.post(url, data={"text": "test option"}, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["text"] == "test option"
    assert response.data["order"] == 1
    assert response.data["question"] == question.id


def test_option_create_invalid_data(api_client, admin_user, question):
    url = reverse("surveys:option-list", kwargs={"question_pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.post(url, data={"text": ""}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_option_list(api_client, admin_user, question):
    OptionFactory.create_batch(5, auto_order=True, question=question)
    url = reverse("surveys:option-list", kwargs={"question_pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 5
    assert len(response.data["results"]) == 5


def test_option_detail(api_client, admin_user, question):
    option = OptionFactory.create(auto_order=True, question=question)
    url = reverse(
        "surveys:option-detail",
        kwargs={"question_pk": str(question.id), "pk": str(option.id)},
    )
    api_client.force_authenticate(admin_user)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(option.id)


def test_option_update(api_client, admin_user, question):
    data = {"question": str(question.id), "text": "new text", "order": 2}
    option = OptionFactory.create(auto_order=True, question=question)
    url = reverse(
        "surveys:option-detail",
        kwargs={"question_pk": str(question.id), "pk": str(option.id)},
    )
    api_client.force_authenticate(admin_user)
    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(option.id)
    assert response.data["text"] == data["text"]
    assert response.data["order"] == data["order"]


def test_option_partial_update(api_client, admin_user, question):
    option = OptionFactory.create(auto_order=True, question=question)
    url = reverse(
        "surveys:option-detail",
        kwargs={"question_pk": str(question.id), "pk": str(option.id)},
    )
    api_client.force_authenticate(admin_user)
    response = api_client.patch(url, data={"text": "new text"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(option.id)
    assert response.data["text"] == "new text"
    assert response.data["order"] == option.order


def test_option_delete(api_client, admin_user, question):
    option = OptionFactory.create(auto_order=True, question=question)
    url = reverse(
        "surveys:option-detail",
        kwargs={"question_pk": str(question.id), "pk": str(option.id)},
    )
    api_client.force_authenticate(admin_user)
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Option.objects.filter(id=option.id).exists()
