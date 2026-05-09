import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.models import User

pytestmark = pytest.mark.django_db

data = {"email": "test@email.com"}


def test_create_respondent(admin_api_client):
    url = reverse("users:respondent_create")
    response = admin_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["email"] == data["email"]


def test_create_respondent_created_by(admin_api_client):
    url = reverse("users:respondent_create")
    response = admin_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(id=response.data["id"])
    assert user.created_by is not None
    # User.__str__() retorna email, usado aqui
    assert User.objects.filter(email=user.created_by).exists()


def test_create_respondent_requires_auth(api_client):
    url = reverse("users:respondent_create")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_respondent_denied(api_client, respondent_user):
    api_client.force_authenticate(respondent_user)
    url = reverse("users:respondent_create")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_respondent_invalid_data(admin_api_client):
    url = reverse("users:respondent_create")
    data = {"email": ""}
    response = admin_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
