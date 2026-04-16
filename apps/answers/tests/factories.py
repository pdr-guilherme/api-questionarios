import factory

from apps.answers.models import SurveyAccess
from apps.surveys.tests.factories import SurveyFactory
from apps.users.tests.factories import UserFactory


class SurveyAccessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SurveyAccess

    user = factory.SubFactory(UserFactory)
    survey = factory.SubFactory(SurveyFactory)
