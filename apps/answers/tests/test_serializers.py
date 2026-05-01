import pytest

from apps.answers.api.serializers import (
    AnswerSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer,
)
from apps.answers.models import Answer, Submission
from apps.answers.tests.factories import (
    SubmissionFactory,
    SurveyAccessFactory,
)
from apps.surveys.tests.factories import OptionFactory, QuestionFactory

pytestmark = pytest.mark.django_db


def test_submission_to_list_serializer(submission):
    serializer = SubmissionListSerializer(submission)
    assert isinstance(serializer.data, dict)

    fields = ["id", "survey", "survey_title", "status", "started_at", "finished_at"]
    for field in fields:
        assert field in serializer.data


def test_submission_to_detail_serializer(submission):
    serializer = SubmissionDetailSerializer(submission)
    assert isinstance(serializer.data, dict)

    fields = [
        "id",
        "survey",
        "survey_title",
        "status",
        "started_at",
        "finished_at",
        "created_at",
        "updated_at",
        "answers",
    ]
    for field in fields:
        assert field in serializer.data


def test_submission_detail_serializer_empty_answers(submission):
    serializer = SubmissionDetailSerializer(submission)
    assert isinstance(serializer.data, dict)

    assert serializer.data["answers"] == []


def test_serializer_to_submission(respondent_user, respondent_context):
    survey_access = SurveyAccessFactory(user=respondent_user)
    data = {"survey": str(survey_access.survey.id)}
    serializer = SubmissionListSerializer(data=data, context=respondent_context)
    assert serializer.is_valid(), serializer.errors

    submission = serializer.save()
    assert isinstance(submission, Submission)
    assert submission.status == Submission.StatusChoices.DRAFT
    assert submission.started_at is not None
    assert submission.finished_at is None


def test_submission_list_serializer_read_only_fields(
    respondent_user, respondent_context
):
    fake_date = "2000-01-01T00:00:00Z"
    survey_access = SurveyAccessFactory(user=respondent_user)
    data = {
        "survey": str(survey_access.survey.id),
        "id": "90dc1281-cbd9-4168-ba46-5e56434056c3",
        "started_at": fake_date,
        "finished_at": fake_date,
        "status": Submission.StatusChoices.COMPLETED,
    }
    serializer = SubmissionListSerializer(data=data, context=respondent_context)
    assert serializer.is_valid(), serializer.errors

    assert "id" not in serializer.validated_data  # type: ignore
    assert "started_at" not in serializer.validated_data  # type: ignore
    assert "finished_at" not in serializer.validated_data  # type: ignore
    assert "status" not in serializer.validated_data  # type: ignore


def test_answer_to_serializer(answer):
    serializer = AnswerSerializer(answer)
    assert isinstance(serializer.data, dict)

    fields = [
        "id",
        "question",
        "question_text",
        "option",
        "option_text",
        "answered_at",
    ]
    for field in fields:
        assert field in serializer.data


def test_serializer_to_answer():
    sub = SubmissionFactory()
    question = QuestionFactory(survey=sub.survey)
    option = OptionFactory(question=question)
    data = {
        "submission": str(sub.id),
        "question": str(question.id),
        "option": str(option.id),
    }
    serializer = AnswerSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    sub.status = Submission.StatusChoices.DRAFT
    sub.refresh_from_db()
    answer = serializer.save(submission=sub)
    assert isinstance(answer, Answer)
    assert answer.answered_at is not None
