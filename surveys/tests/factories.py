import factory

from surveys.models import Survey
from users.tests.factories import UserFactory


class SurveyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Survey

    author = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Survey {n}")
    status = Survey.StatusChoices.DRAFT
