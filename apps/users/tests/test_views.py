from typing import cast

import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.models import User
from apps.users.tests.factories import AdminFactory, UserFactory

pytestmark = pytest.mark.django_db

data = {"email": "test@email.com"}


@pytest.fixture
def respondents(admin_user):
    return [cast(User, UserFactory(created_by=admin_user)) for _ in range(3)]


@pytest.fixture
def other_respondents():
    other_admin = AdminFactory()
    return [cast(User, UserFactory(created_by=other_admin)) for _ in range(3)]


def test_create_respondent(admin_api_client):
    url = reverse("users:respondent-list")
    response = admin_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["email"] == data["email"]


def test_create_respondent_created_by(admin_api_client):
    url = reverse("users:respondent-list")
    response = admin_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(id=response.data["id"])
    assert user.created_by is not None
    # User.__str__() retorna email, usado aqui
    assert User.objects.filter(email=user.created_by).exists()


def test_create_respondent_requires_auth(api_client):
    url = reverse("users:respondent-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_respondent_denied(api_client, respondent_user):
    api_client.force_authenticate(respondent_user)
    url = reverse("users:respondent-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_respondent_invalid_data(admin_api_client):
    url = reverse("users:respondent-list")
    data = {"email": ""}
    response = admin_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_respondent_list(admin_api_client, respondents):
    url = reverse("users:respondent-list")
    response = admin_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == len(respondents)
    assert len(response.data["results"]) == len(respondents)


def test_respondent_detail(admin_api_client, respondent_user):
    url = reverse("users:respondent-detail", kwargs={"pk": str(respondent_user.id)})
    response = admin_api_client.get(url)
    fields = [
        "id",
        "email",
        "created_at",
        "updated_at",
        "is_active",
        "last_login",
    ]

    assert response.status_code == status.HTTP_200_OK
    for field in fields:
        assert field in response.data


def test_respondent_list_isolated_respondents(
    admin_api_client, respondents, other_respondents
):
    url = reverse("users:respondent-list")
    response = admin_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    returned_ids = {user["id"] for user in response.data["results"]}
    expected_ids = {str(respondent.id) for respondent in respondents}
    other_ids = {str(other.id) for other in other_respondents}

    assert expected_ids.issubset(returned_ids)
    assert not expected_ids.issubset(other_ids)


def test_respondent_detail_access_other_respondent(admin_api_client, other_respondents):
    other = other_respondents[0]
    url = reverse("users:respondent-detail", kwargs={"pk": str(other.id)})
    response = admin_api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_respondent_list_as_respondent(respondent_api_client):
    url = reverse("users:respondent-list")
    response = respondent_api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_respondent_detail_as_respondent(respondent_api_client, respondent_user):
    url = reverse("users:respondent-detail", kwargs={"pk": str(respondent_user.id)})
    response = respondent_api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_respondent_update(admin_api_client, respondent_user):
    data = {"email": "test@email.com"}
    url = reverse("users:respondent-detail", kwargs={"pk": str(respondent_user.id)})
    response = admin_api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    respondent_user.refresh_from_db()
    assert respondent_user.email == data["email"]


def test_respondent_partial_update(admin_api_client, respondent_user):
    data = {"email": "test@email.com"}
    url = reverse("users:respondent-detail", kwargs={"pk": str(respondent_user.id)})
    response = admin_api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    respondent_user.refresh_from_db()
    assert respondent_user.email == data["email"]
