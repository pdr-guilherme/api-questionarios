import pytest

from apps.surveys.api.serializers import QuestionImageSerializer
from apps.surveys.models import QuestionImage
from apps.surveys.tests.factories import QuestionFactory, QuestionImageFactory
from apps.surveys.tests.helpers import make_image

pytestmark = pytest.mark.django_db


def test_question_image_to_serializer(admin_context):
    question_image = QuestionImageFactory()
    serializer = QuestionImageSerializer(instance=question_image, context=admin_context)

    assert isinstance(serializer.data, dict)
    assert serializer.data["id"] == str(question_image.id)
    assert serializer.data["order"] == question_image.order
    assert serializer.data["file"].startswith("http")


def test_serializer_to_question_image():
    question = QuestionFactory()
    data = {
        "file": make_image(),
        "order": 1,
    }
    serializer = QuestionImageSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question_image = serializer.save(question=question)
    assert isinstance(question_image, QuestionImage)
    assert str(question_image.question.id) == str(question.id)
    assert question_image.order == data["order"]
    assert f"question_images/{question.id}/" in question_image.file.name


def test_question_image_serializer_id_is_read_only():
    question = QuestionFactory()
    data = {
        "file": make_image(),
        "order": 1,
        "id": "b2376b29-dc4e-4a1b-9f7d-826805319ffe",
    }
    serializer = QuestionImageSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question_image = serializer.save(question=question)
    assert isinstance(question_image, QuestionImage)
    assert str(question_image.id) != data["id"]


def test_serializer_without_order_to_question_image():
    question = QuestionFactory()
    data = {
        "file": make_image(),
    }
    serializer = QuestionImageSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question_image = serializer.save(question=question)
    assert isinstance(question_image, QuestionImage)
    assert question_image.order == 1


def test_serializer_to_many_question_images_auto_order():
    question = QuestionFactory()
    data = [
        {"file": make_image(name="file1.jpg")},
        {"file": make_image(name="file2.jpg")},
        {"file": make_image(name="file3.jpg")},
    ]
    serializer = QuestionImageSerializer(data=data, many=True)
    assert serializer.is_valid(), serializer.errors

    question_images = serializer.save(question=question)
    assert isinstance(question_images, list)
    for count, question_image in enumerate(question_images, start=1):
        assert question_image.order == count
