import pytest

from surveys.api.serializers import QuestionDetailSerializer, QuestionSerializer
from surveys.models import Question
from surveys.tests.factories import QuestionFactory, QuestionImageFactory, SurveyFactory
from surveys.tests.helpers import make_image

pytestmark = pytest.mark.django_db


def test_question_to_serializer():
    question = QuestionFactory()
    serializer = QuestionSerializer(instance=question)

    assert isinstance(serializer.data, dict)
    assert serializer.data["id"] == str(question.id)
    assert serializer.data["text"] == question.text
    assert serializer.data["order"] == question.order
    assert serializer.data["is_required"] == question.is_required
    assert serializer.data["survey"] == question.survey.id


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


def test_question_to_question_detail_serializer():
    question = QuestionFactory()
    QuestionImageFactory.create_batch(5, question=question)
    question.refresh_from_db()
    assert question.images.exists()

    question_detail_serializer = QuestionDetailSerializer(instance=question)
    assert isinstance(question_detail_serializer.data, dict)
    assert question_detail_serializer.data["id"] == str(question.id)
    assert "images" in question_detail_serializer.data
    assert isinstance(question_detail_serializer.data["images"], list)


def test_question_detail_serializer_create_images():
    survey = SurveyFactory()
    data = {
        "survey": str(survey.id),
        "text": "test text",
        "images": [
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
    assert question.images.exists()  # type:ignore


def test_question_detail_serializer_create_options():
    survey = SurveyFactory()
    data = {
        "survey": str(survey.id),
        "text": "test text",
        "options": [
            {"text": "option 1"},
            {"text": "option 2"},
            {"text": "option 3"},
        ],
    }
    serializer = QuestionDetailSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    question = serializer.save()
    assert isinstance(question, Question)
    assert question.id is not None
    assert question.options.exists()  # type:ignore
