import factory

from apps.answers.models import Answer, Submission, SurveyAccess
from apps.surveys.models import Survey
from apps.surveys.tests.factories import OptionFactory, QuestionFactory, SurveyFactory
from apps.users.tests.factories import UserFactory


class SurveyAccessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SurveyAccess

    user = factory.SubFactory(UserFactory)
    survey = factory.SubFactory(SurveyFactory, status=Survey.StatusChoices.PUBLISHED)


class SubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Submission
        exclude = ["survey_access"]

    survey_access = factory.SubFactory(SurveyAccessFactory)
    user = factory.SubFactory(UserFactory)
    survey = factory.LazyAttribute(lambda obj: obj.survey_access.survey)
    status = Submission.StatusChoices.DRAFT

    class Params:
        completed = factory.Trait(status=Submission.StatusChoices.COMPLETED)


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Answer
        exclude = ["survey"]

    submission = factory.SubFactory(SubmissionFactory, completed=False)
    survey = factory.LazyAttribute(lambda obj: obj.submission.survey)
    question = factory.LazyAttribute(lambda obj: QuestionFactory(survey=obj.survey))
    option = factory.LazyAttribute(lambda obj: OptionFactory(question=obj.question))
