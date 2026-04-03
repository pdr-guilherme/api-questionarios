import factory

from surveys.models import Question, Survey
from users.tests.factories import UserFactory


class SurveyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Survey

    author = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Survey {n}")
    status = Survey.StatusChoices.DRAFT


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    survey = factory.SubFactory(SurveyFactory)
    text = factory.Faker("sentence")
    order = factory.Sequence(int)

    @classmethod
    def _setup_next_sequence(cls):
        try:
            return Question.objects.latest("order").order + 1
        except Question.DoesNotExist:
            return 1
