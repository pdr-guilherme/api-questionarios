from io import BytesIO
from typing import cast

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from PIL import Image

from surveys.models import Question, Survey
from surveys.tests.factories import (
    OptionFactory,
    QuestionFactory,
    QuestionImageFactory,
    SurveyFactory,
)
from surveys.tests.helpers import make_image


@pytest.mark.django_db
def test_survey_to_str():
    survey = SurveyFactory.build()
    assert str(survey) == survey.title


@pytest.mark.django_db
def test_survey_transition_to_valid():
    survey = cast(Survey, SurveyFactory(status=Survey.StatusChoices.DRAFT))
    survey.transition_to(Survey.StatusChoices.PUBLISHED)
    assert survey.status == Survey.StatusChoices.PUBLISHED


@pytest.mark.django_db
def test_survey_transition_to_invalid():
    survey = cast(Survey, SurveyFactory(status=Survey.StatusChoices.DRAFT))
    with pytest.raises(ValidationError, match="inválida"):
        survey.transition_to(Survey.StatusChoices.CLOSED)


@pytest.mark.django_db
def test_question_to_str():
    question = QuestionFactory.build()
    assert str(question) == question.text


@pytest.mark.django_db
def test_question_unique_survey_order_valid():
    survey = SurveyFactory()
    question1 = QuestionFactory(survey=survey, order=1)
    question2 = QuestionFactory(survey=survey, order=2)

    assert question1.order != question2.order


@pytest.mark.django_db
def test_question_unique_survey_order_invalid():
    survey = SurveyFactory()
    QuestionFactory(survey=survey, order=1)

    with pytest.raises(IntegrityError):
        QuestionFactory(survey=survey, order=1)


@pytest.mark.django_db
def test_question_order_must_be_greater_than_zero():
    survey = SurveyFactory()
    question = QuestionFactory.build(survey=survey, order=0)
    with pytest.raises(ValidationError):
        question.full_clean()


@pytest.mark.django_db
def test_question_ordering_within_survey():
    survey = SurveyFactory()

    question1 = QuestionFactory(survey=survey, order=2)
    question2 = QuestionFactory(survey=survey, order=1)
    question3 = QuestionFactory(survey=survey, order=3)

    questions = list(survey.questions.all())

    assert questions == [question2, question1, question3]


@pytest.mark.django_db
def test_question_order_is_isolated_per_survey():
    survey1 = SurveyFactory(title="A")
    survey2 = SurveyFactory(title="B")

    question1 = QuestionFactory(survey=survey1, order=1)
    question2 = QuestionFactory(survey=survey1, order=2)

    question3 = QuestionFactory(survey=survey2, order=1)

    question_list1 = list(survey1.questions.all())
    question_list2 = list(survey2.questions.all())

    assert question_list1 == [question1, question2]
    assert question_list2 == [question3]


@pytest.mark.django_db
def test_auto_increment_order():
    survey = SurveyFactory()

    question1 = Question.objects.create(survey=survey, text="test text")
    question2 = Question.objects.create(survey=survey, text="test text")
    question3 = Question.objects.create(survey=survey, text="test text")

    assert question1.order == 1
    assert question2.order == 2
    assert question3.order == 3


@pytest.mark.django_db
def test_question_image_to_str():
    question_image = QuestionImageFactory()
    assert "Image for question" in str(question_image)
    assert str(question_image.question) in str(question_image)
    assert str(question_image.order) in str(question_image)


@pytest.mark.django_db
def test_question_image_file_resize():
    question_image = QuestionImageFactory(file=make_image(size=(1200, 1200)))
    question_image.file.open()
    img = Image.open(question_image.file)

    assert img.width <= 800
    assert img.height <= 800


@pytest.mark.django_db
def test_question_image_small_file_remains_intact():
    question_image = QuestionImageFactory(file=make_image(size=(400, 400)))
    question_image.file.open()
    img = Image.open(question_image.file)

    assert img.width == 400
    assert img.height == 400


@pytest.mark.django_db
def test_question_image_file_saves_as_jpeg():
    question_image = QuestionImageFactory(
        file=make_image(name="file.png", format="png")
    )
    assert question_image.file.name.endswith(".jpg")


@pytest.mark.django_db
def test_question_image_ordering_within_question():
    question = QuestionFactory()

    question_image1 = QuestionImageFactory(question=question, order=2)
    question_image2 = QuestionImageFactory(question=question, order=1)
    question_image3 = QuestionImageFactory(question=question, order=3)

    question_images = list(question.question_images.all())
    assert question_images == [question_image2, question_image1, question_image3]


@pytest.mark.django_db
def test_question_image_order_is_isolated_per_question():
    question1 = QuestionFactory(text="A")
    question2 = QuestionFactory(text="B")

    question_image1 = QuestionImageFactory(question=question1, auto_order=True)
    question_image2 = QuestionImageFactory(question=question1, auto_order=True)
    question_image3 = QuestionImageFactory(question=question2, auto_order=True)

    image_list1 = list(question1.question_images.all())
    image_list2 = list(question2.question_images.all())

    assert image_list1 == [question_image1, question_image2]
    assert image_list2 == [question_image3]


@pytest.mark.django_db
def test_question_image_auto_increment_order():
    question = QuestionFactory()

    question_image1 = QuestionImageFactory(question=question, auto_order=True)
    question_image2 = QuestionImageFactory(question=question, auto_order=True)
    question_image3 = QuestionImageFactory(question=question, auto_order=True)

    assert question_image1.order == 1
    assert question_image2.order == 2
    assert question_image3.order == 3


@pytest.mark.django_db
def test_question_image_rgba_to_rgb_conversion():
    buffer = BytesIO()
    Image.new("RGBA", (100, 100), (255, 0, 0, 128)).save(buffer, format="PNG")
    buffer.seek(0)
    file = SimpleUploadedFile("image.png", buffer.read(), content_type="image/png")
    question_image = QuestionImageFactory(file=file)
    # chegou aqui => conversão funcionou
    assert question_image.file.name is not None


@pytest.mark.django_db
def test_option_to_str():
    option = OptionFactory()
    expected = f'Option {option.order} for question "{option.question}": {option.text}'
    assert str(option) == expected


@pytest.mark.django_db
def test_option_ordering_within_question():
    question = QuestionFactory()
    option1 = OptionFactory(question=question, order=2)
    option2 = OptionFactory(question=question, order=1)
    option3 = OptionFactory(question=question, order=3)

    question_images = list(question.options.all())
    assert question_images == [option2, option1, option3]


@pytest.mark.django_db
def test_option_order_is_isolated_per_question():
    question1 = QuestionFactory(text="A")
    question2 = QuestionFactory(text="B")

    option1 = OptionFactory(question=question1, auto_order=True)
    option2 = OptionFactory(question=question1, auto_order=True)
    option3 = OptionFactory(question=question2, auto_order=True)

    option_list1 = list(question1.options.all())
    option_list2 = list(question2.options.all())

    assert option_list1 == [option1, option2]
    assert option_list2 == [option3]


@pytest.mark.django_db
def test_option_auto_increment_order():
    question1 = QuestionFactory(text="A")

    option1 = OptionFactory(question=question1, auto_order=True)
    option2 = OptionFactory(question=question1, auto_order=True)
    option3 = OptionFactory(question=question1, auto_order=True)

    assert option1.order == 1
    assert option2.order == 2
    assert option3.order == 3


@pytest.mark.django_db
def test_option_unique_question_option_order():
    question = QuestionFactory()
    OptionFactory(question=question, order=1)

    with pytest.raises(IntegrityError):
        OptionFactory(question=question, order=1)
