import pytest
from django.urls import reverse
from rest_framework import status

from apps.surveys.models import QuestionImage
from apps.surveys.tests.factories import QuestionImageFactory
from apps.surveys.tests.helpers import make_image

pytestmark = pytest.mark.django_db


def test_question_image_create(api_client, admin_user, question):
    data = {
        "file": make_image(),
        "alt_text": "test image",
    }
    url = reverse("surveys:image-list", kwargs={"question_pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.post(url, data=data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    assert "file" in response.data
    assert response.data["alt_text"] == data["alt_text"]
    assert response.data["order"] == 1


def test_question_image_create_invalid_data(api_client, admin_user, question):
    from django.core.files.uploadedfile import SimpleUploadedFile

    arquivo = SimpleUploadedFile("doc.txt", b"conteudo", content_type="text/plain")
    data1 = {"question": str(question.id)}
    data2 = {"question": str(question.id), "file": arquivo}
    url = reverse("surveys:image-list", kwargs={"question_pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response1 = api_client.post(url, data=data1, format="multipart")
    response2 = api_client.post(url, data=data2, format="multipart")

    assert response1.status_code == status.HTTP_400_BAD_REQUEST
    assert response2.status_code == status.HTTP_400_BAD_REQUEST


def test_question_image_list(api_client, admin_user, question):
    QuestionImageFactory.create_batch(3, auto_order=True, question=question)
    url = reverse("surveys:image-list", kwargs={"question_pk": str(question.id)})
    api_client.force_authenticate(admin_user)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3
    assert len(response.data["results"]) == 3


def test_question_image_detail(api_client, admin_user, question):
    question_image = QuestionImageFactory.create(auto_order=True, question=question)
    url = reverse(
        "surveys:image-detail",
        kwargs={"question_pk": str(question.id), "pk": str(question_image.id)},
    )
    api_client.force_authenticate(admin_user)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(question_image.id)


def test_question_image_update(api_client, admin_user, question):
    question_image = QuestionImageFactory.create(auto_order=True, question=question)
    data = {
        "question": str(question.id),
        "file": make_image(),
        "alt_text": "test image",
        "order": 2,
    }
    url = reverse(
        "surveys:image-detail",
        kwargs={"question_pk": str(question.id), "pk": str(question_image.id)},
    )
    api_client.force_authenticate(admin_user)
    response = api_client.put(url, data=data, format="multipart")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(question_image.id)
    assert response.data["alt_text"] == data["alt_text"]
    assert response.data["order"] == data["order"]


def test_question_image_partial_update(api_client, admin_user, question):
    question_image = QuestionImageFactory.create(auto_order=True, question=question)
    data = {"order": 2}
    url = reverse(
        "surveys:image-detail",
        kwargs={"question_pk": str(question.id), "pk": str(question_image.id)},
    )
    api_client.force_authenticate(admin_user)
    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(question_image.id)
    assert response.data["alt_text"] == question_image.alt_text
    assert response.data["order"] == data["order"]


def test_question_image_delete(api_client, admin_user, question):
    question_image = QuestionImageFactory.create(auto_order=True, question=question)
    url = reverse(
        "surveys:image-detail",
        kwargs={"question_pk": str(question.id), "pk": str(question_image.id)},
    )
    api_client.force_authenticate(admin_user)
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not QuestionImage.objects.filter(pk=question_image.id).exists()
