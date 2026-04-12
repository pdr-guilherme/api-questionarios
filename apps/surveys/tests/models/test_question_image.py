from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.surveys.tests.factories import QuestionFactory, QuestionImageFactory
from apps.surveys.tests.helpers import make_image

pytestmark = pytest.mark.django_db


def test_question_image_to_str():
    question_image = QuestionImageFactory()
    assert "Image for question" in str(question_image)
    assert str(question_image.question) in str(question_image)
    assert str(question_image.order) in str(question_image)


def test_question_image_file_resize():
    question_image = QuestionImageFactory(file=make_image(size=(1200, 1200)))
    question_image.file.open()
    img = Image.open(question_image.file)

    assert img.width <= 800
    assert img.height <= 800


def test_question_image_small_file_remains_intact():
    question_image = QuestionImageFactory(file=make_image(size=(400, 400)))
    question_image.file.open()
    img = Image.open(question_image.file)

    assert img.width == 400
    assert img.height == 400


def test_question_image_file_saves_as_jpeg():
    question_image = QuestionImageFactory(
        file=make_image(name="file.png", format="png")
    )
    assert question_image.file.name.endswith(".jpg")


def test_question_image_ordering_within_question():
    question = QuestionFactory()

    question_image1 = QuestionImageFactory(question=question, order=2)
    question_image2 = QuestionImageFactory(question=question, order=1)
    question_image3 = QuestionImageFactory(question=question, order=3)

    images = list(question.images.all())
    assert images == [question_image2, question_image1, question_image3]


def test_question_image_order_is_isolated_per_question():
    question1 = QuestionFactory(text="A")
    question2 = QuestionFactory(text="B")

    question_image1 = QuestionImageFactory(question=question1, auto_order=True)
    question_image2 = QuestionImageFactory(question=question1, auto_order=True)
    question_image3 = QuestionImageFactory(question=question2, auto_order=True)

    image_list1 = list(question1.images.all())
    image_list2 = list(question2.images.all())

    assert image_list1 == [question_image1, question_image2]
    assert image_list2 == [question_image3]


def test_question_image_auto_increment_order():
    question = QuestionFactory()

    question_image1 = QuestionImageFactory(question=question, auto_order=True)
    question_image2 = QuestionImageFactory(question=question, auto_order=True)
    question_image3 = QuestionImageFactory(question=question, auto_order=True)

    assert question_image1.order == 1
    assert question_image2.order == 2
    assert question_image3.order == 3


def test_question_image_rgba_to_rgb_conversion():
    buffer = BytesIO()
    Image.new("RGBA", (100, 100), (255, 0, 0, 128)).save(buffer, format="PNG")
    buffer.seek(0)
    file = SimpleUploadedFile("image.png", buffer.read(), content_type="image/png")
    question_image = QuestionImageFactory(file=file)
    # chegou aqui => conversão funcionou
    assert question_image.file.name is not None
    question_image = QuestionImageFactory(file=file)
    # chegou aqui => conversão funcionou
    assert question_image.file.name is not None
