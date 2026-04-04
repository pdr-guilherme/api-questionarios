import pytest

from surveys.api.serializers import (
    QuestionDetailSerializer,
    QuestionImageSerializer,
    QuestionSerializer,
    SurveySerializer,
)
from surveys.models import Question, QuestionImage, Survey
from surveys.tests.factories import QuestionFactory, QuestionImageFactory, SurveyFactory
from surveys.tests.helpers import make_image


@pytest.fixture
def context(request_factory, admin_user):
    request = request_factory.post("/")
    request.user = admin_user
    return {"request": request}


@pytest.mark.django_db
def test_survey_to_serializer(context):
    survey = SurveyFactory()
    serializer = SurveySerializer(instance=survey, context=context)
    assert serializer.data["title"] == survey.title  # type:ignore


@pytest.mark.django_db
def test_serializer_to_survey(context):
    data = {"title": "minha pesquisa", "status": Survey.StatusChoices.DRAFT}
    serializer = SurveySerializer(data=data, context=context)
    assert serializer.is_valid(), serializer.errors

    survey = serializer.save()
    assert isinstance(survey, Survey)
    assert survey.title == data["title"]
    assert survey.status == data["status"]


@pytest.mark.django_db
def test_survey_serializer_data_invalid(context):
    data = {"title": None, "status": Survey.StatusChoices.DRAFT}
    serializer = SurveySerializer(data=data, context=context)
    assert not serializer.is_valid(), serializer.errors
    assert "title" in serializer.errors


@pytest.mark.django_db
def test_question_to_serializer():
    question = QuestionFactory()
    serializer = QuestionSerializer(instance=question)

    assert isinstance(serializer.data, dict)
    assert serializer.data["id"] == str(question.id)
    assert serializer.data["text"] == question.text
    assert serializer.data["order"] == question.order
    assert serializer.data["is_required"] == question.is_required
    assert serializer.data["survey"] == question.survey.id


@pytest.mark.django_db
def test_serializer_to_question():
    survey = SurveyFactory()
    data = {
        "survey": str(survey.id),
        "text": "test text",
        "order": 1,
        "is_required": True,
    }
    serializer = QuestionSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question = serializer.save()
    assert isinstance(question, Question)
    assert question.text == data["text"]
    assert question.order == data["order"]
    assert question.is_required == data["is_required"]
    assert str(question.survey.id) == data["survey"]


@pytest.mark.django_db
def test_question_serializer_id_is_read_only():
    survey = SurveyFactory()
    data = {
        "survey": str(survey.id),
        "text": "test text",
        "order": 1,
        "is_required": True,
        "id": "b2376b29-dc4e-4a1b-9f7d-826805319ffe",
    }
    serializer = QuestionSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question = serializer.save()
    assert isinstance(question, Question)
    assert str(question.id) != data["id"]


@pytest.mark.django_db
def test_serializer_to_question_default_is_required():
    survey = SurveyFactory()
    data = {
        "survey": str(survey.id),
        "text": "test text",
        "order": 1,
        "is_required": True,
    }
    serializer = QuestionSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question = serializer.save()
    assert isinstance(question, Question)
    assert question.is_required


@pytest.mark.django_db
def test_serializer_without_order_to_question():
    survey = SurveyFactory()
    data = {
        "survey": str(survey.id),
        "text": "test text",
        "is_required": True,
    }
    serializer = QuestionSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question = serializer.save()
    assert isinstance(question, Question)
    assert question.order == 1


@pytest.mark.django_db
def test_serializer_to_many_questions_auto_order():
    survey = SurveyFactory()
    data = [
        {
            "survey": str(survey.id),
            "text": "test text",
            "is_required": True,
        },
        {
            "survey": str(survey.id),
            "text": "test text 2",
            "is_required": True,
        },
        {
            "survey": str(survey.id),
            "text": "test text 3",
            "is_required": True,
        },
    ]

    serializer = QuestionSerializer(data=data, many=True)
    assert serializer.is_valid(), serializer.errors

    questions = serializer.save()
    assert isinstance(questions, list)
    for count, question in enumerate(questions, start=1):
        assert question.order == count


@pytest.mark.django_db
def test_serializer_to_question_invalid_data():
    survey = SurveyFactory()
    data = {
        "survey": str(survey.id),
        "text": "",  # não pode ser vazio
        "is_required": True,
    }
    serializer = QuestionSerializer(data=data)
    assert not serializer.is_valid(), serializer.errors
    assert "text" in serializer.errors


@pytest.mark.django_db
def test_question_image_to_serializer(context):
    question_image = QuestionImageFactory()
    serializer = QuestionImageSerializer(instance=question_image, context=context)

    assert isinstance(serializer.data, dict)
    assert serializer.data["id"] == str(question_image.id)
    assert serializer.data["order"] == question_image.order
    assert serializer.data["file"].startswith("http")


@pytest.mark.django_db
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


@pytest.mark.django_db
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


@pytest.mark.django_db
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


@pytest.mark.django_db
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
    for count, question_images in enumerate(question_images, start=1):
        assert question_images.order == count


@pytest.mark.django_db
def test_question_to_question_detail_serializer():
    question = QuestionFactory()
    QuestionImageFactory.create_batch(5, question=question)
    question.refresh_from_db()
    assert question.question_images.exists()

    question_detail_serializer = QuestionDetailSerializer(instance=question)
    assert isinstance(question_detail_serializer.data, dict)
    assert question_detail_serializer.data["id"] == str(question.id)
    assert "question_images" in question_detail_serializer.data
    assert isinstance(question_detail_serializer.data["question_images"], list)


@pytest.mark.django_db
def test_question_detail_serializer_create_images():
    survey = SurveyFactory()
    data = {
        "survey": str(survey.id),
        "text": "test text",
        "question_images": [
            {"file": make_image(name="file1.jpg")},
            {"file": make_image(name="file2.jpg")},
            {"file": make_image(name="file3.jpg")},
        ],
    }
    serializer = QuestionDetailSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question = serializer.save()
    assert isinstance(question, Question)
    assert question.id is not None
    assert question.question_images.exists()  # type:ignore
