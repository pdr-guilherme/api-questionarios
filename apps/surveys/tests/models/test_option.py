import pytest
from django.db import IntegrityError

from apps.surveys.tests.factories import OptionFactory, QuestionFactory

pytestmark = pytest.mark.django_db


def test_option_to_str():
    option = OptionFactory()
    expected = f'Option {option.order} for question "{option.question}": {option.text}'
    assert str(option) == expected


def test_option_ordering_within_question():
    question = QuestionFactory()
    option1 = OptionFactory(question=question, order=2)
    option2 = OptionFactory(question=question, order=1)
    option3 = OptionFactory(question=question, order=3)

    question_images = list(question.options.all())
    assert question_images == [option2, option1, option3]


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


def test_option_auto_increment_order():
    question1 = QuestionFactory(text="A")

    option1 = OptionFactory(question=question1, auto_order=True)
    option2 = OptionFactory(question=question1, auto_order=True)
    option3 = OptionFactory(question=question1, auto_order=True)

    assert option1.order == 1
    assert option2.order == 2
    assert option3.order == 3


def test_option_unique_question_option_order():
    question = QuestionFactory()
    OptionFactory(question=question, order=1)

    with pytest.raises(IntegrityError):
        OptionFactory(question=question, order=1)
