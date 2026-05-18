import pytest

from apps.answers.api.serializers import (
    AnswerSerializer,
    QuestionProgressSerializer,
    RespondentProgressDetailSerializer,
    RespondentProgressListSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer,
    SurveyProgressDetailSerializer,
    SurveyProgressListSerializer,
)
from apps.answers.models import Answer, Submission
from apps.answers.tests.factories import (
    AnswerFactory,
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


def test_survey_to_survey_progress_list_serializer(admin_survey, admin_submissions):
    serializer = SurveyProgressListSerializer(admin_survey)
    assert isinstance(serializer.data, dict)

    fields = [
        "id",
        "title",
        "status",
        "total_respondents",
        "not_started",
        "in_progress",
        "completed",
        "completion_rate",
    ]
    for field in fields:
        assert field in serializer.data

    assert serializer.data["total_respondents"] == 3
    assert serializer.data["not_started"] == 0
    assert serializer.data["in_progress"] == 3
    assert serializer.data["completed"] == 0
    assert serializer.data["completion_rate"] == 0


def test_survey_progress_detail_serializer(admin_survey, admin_submissions):
    serializer = SurveyProgressDetailSerializer(admin_survey)
    assert isinstance(serializer.data, dict)

    fields = [
        "id",
        "title",
        "status",
        "total_respondents",
        "not_started",
        "in_progress",
        "completed",
        "completion_rate",
        "created_at",
        "updated_at",
    ]

    for field in fields:
        assert field in serializer.data


def test_question_progress_serializer(answer):
    question = answer.question
    serializer = QuestionProgressSerializer(question, context={"answers": [answer]})
    assert isinstance(serializer.data, dict)

    fields = ["id", "text", "order", "is_required", "answered", "answer"]
    for field in fields:
        assert field in serializer.data

    assert serializer.data["answered"]
    assert isinstance(serializer.data["answer"], dict)


def test_question_progress_serializer_no_answer(answer):
    serializer = QuestionProgressSerializer(answer.question)
    assert isinstance(serializer.data, dict)

    assert serializer.data["answer"] is None


def test_respondent_progress_list_serializer(admin_accesses, admin_submissions):
    admin_submission = admin_submissions[0]
    admin_survey_access = admin_accesses[0]

    serializer = RespondentProgressListSerializer(admin_survey_access)
    assert isinstance(serializer.data, dict)

    fields = [
        "user_id",
        "email",
        "status",
        "progress_percentage",
        "unanswered_required_count",
        "started_at",
        "finished_at",
    ]
    for field in fields:
        assert field in serializer.data

    user = admin_survey_access.user
    assert serializer.data["user_id"] == str(user.id)
    assert serializer.data["email"] == user.email
    assert serializer.data["status"] == admin_submission.status
    # survey da fixture não tem perguntas atreladas a ela > resulta nisso
    assert serializer.data["progress_percentage"] == 100
    assert serializer.data["unanswered_required_count"] == 0
    assert serializer.data["started_at"] == admin_submission.started_at
    assert serializer.data["finished_at"] == admin_submission.finished_at


def test_respondent_progress_list_serializer_no_submission(admin_accesses):
    admin_survey_access = admin_accesses[0]
    serializer = RespondentProgressListSerializer(admin_survey_access)
    assert isinstance(serializer.data, dict)

    required_count = admin_survey_access.survey.questions.count()
    assert serializer.data["progress_percentage"] == 0.0
    assert serializer.data["status"] == "not_started"
    assert serializer.data["unanswered_required_count"] == required_count


def test_respondent_progress_detail_serializer(admin_accesses, admin_submissions):
    admin_submission = admin_submissions[0]
    admin_survey_access = admin_accesses[0]

    questions = QuestionFactory.create_batch(3, survey=admin_survey_access.survey)
    for question in questions:
        AnswerFactory(
            question=question, submission=admin_submission, survey=admin_survey_access
        )

    serializer = RespondentProgressDetailSerializer(admin_survey_access)
    assert isinstance(serializer.data, dict)

    fields = [
        "user_id",
        "email",
        "status",
        "progress_percentage",
        "unanswered_required_count",
        "started_at",
        "finished_at",
        "questions",
    ]
    for field in fields:
        assert field in serializer.data

    assert isinstance(serializer.data["questions"], list)
