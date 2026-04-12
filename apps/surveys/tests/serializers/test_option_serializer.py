import pytest

from apps.surveys.api.serializers import OptionSerializer
from apps.surveys.models import Option
from apps.surveys.tests.factories import OptionFactory, QuestionFactory

pytestmark = pytest.mark.django_db


def test_option_to_serializer():
    option = OptionFactory()
    serializer = OptionSerializer(instance=option)

    assert isinstance(serializer.data, dict)
    assert serializer.data["text"] == option.text
    assert serializer.data["id"] == str(option.id)
    assert serializer.data["order"] == option.order


def test_serializer_to_option():
    question = QuestionFactory()
    data = {"text": "test text", "order": 1}
    serializer = OptionSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    option = serializer.save(question=question)
    assert isinstance(option, Option)
    assert option.text == data["text"]
    assert str(option.question_id) == str(question.id)  # type: ignore
    assert option.order == data["order"]


def test_option_serializer_id_is_read_only():
    question = QuestionFactory()
    data = {
        "text": "test text",
        "order": 1,
        "id": "b2376b29-dc4e-4a1b-9f7d-826805319ffe",
    }
    serializer = OptionSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    option = serializer.save(question=question)
    assert isinstance(option, Option)
    assert str(option.id) != data["id"]


def test_serializer_without_order_to_option():
    question = QuestionFactory()
    data = {"text": "test text"}
    serializer = OptionSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    option = serializer.save(question=question)
    assert isinstance(option, Option)
    assert option.order == 1


def test_serializer_to_many_options_auto_order():
    question = QuestionFactory()
    data = [
        {"text": "test text 1"},
        {"text": "test text 2"},
        {"text": "test text 3"},
    ]
    serializer = OptionSerializer(data=data, many=True)
    assert serializer.is_valid(), serializer.errors

    options = serializer.save(question=question)
    assert isinstance(options, list)
    for count, option in enumerate(options, start=1):
        assert option.order == count
