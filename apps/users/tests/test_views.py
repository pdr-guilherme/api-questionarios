import pytest
from django.urls import reverse
from rest_framework import status

data = {"email": "test@email.com"}


@pytest.mark.django_db
def test_create_respondent(admin_api_client):
    url = reverse("users:respondent_create")
    response = admin_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["email"] == data["email"]


def test_create_respondent_requires_auth(api_client):
    url = reverse("users:respondent_create")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_respondent_denied(api_client, respondent_user):
    api_client.force_authenticate(respondent_user)
    url = reverse("users:respondent_create")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_respondent_invalid_data(admin_api_client):
    url = reverse("users:respondent_create")
    data = {"email": ""}
    response = admin_api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
