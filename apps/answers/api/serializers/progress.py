from datetime import datetime
from typing import TypedDict
from uuid import UUID

from rest_framework import serializers

from apps.answers.models import Submission, SurveyAccess
from apps.surveys.models import Question, Survey


class SurveyProgressListSerializer(serializers.ModelSerializer):
    total_respondents = serializers.SerializerMethodField()
    not_started = serializers.SerializerMethodField()
    in_progress = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = Survey
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

    def get_total_respondents(self, obj) -> int:
        return obj.accesses.count()

    def get_not_started(self, obj) -> int:
        respondents_with_submission = obj.submissions.values_list("user_id", flat=True)
        # surveyaccess mas sem submission
        return obj.accesses.exclude(user_id__in=respondents_with_submission).count()

    def get_in_progress(self, obj) -> int:
        return obj.submissions.filter(status=Submission.StatusChoices.DRAFT).count()

    def get_completed(self, obj) -> int:
        return obj.submissions.filter(status=Submission.StatusChoices.COMPLETED).count()

    def get_completion_rate(self, obj) -> float:
        completed = self.get_completed(obj)
        total_respondents = self.get_total_respondents(obj)

        if completed == 0 or total_respondents == 0:
            return 0

        return round((completed / total_respondents) * 100, 1)


class SurveyProgressDetailSerializer(SurveyProgressListSerializer):
    class Meta(SurveyProgressListSerializer.Meta):
        fields = [
            *SurveyProgressListSerializer.Meta.fields,
            "created_at",
            "updated_at",
        ]


class RespondentProgressListSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    status = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    unanswered_required_count = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    finished_at = serializers.SerializerMethodField()

    class Meta:
        model = SurveyAccess
        fields = [
            "user_id",
            "email",
            "status",
            "progress_percentage",
            "unanswered_required_count",
            "started_at",
            "finished_at",
        ]

    def _get_submission(self, obj):
        submissions = obj.user.submissions.all()
        return next(
            (sub for sub in submissions if sub.survey_id == obj.survey_id), None
        )

    def get_status(self, obj) -> str:
        submission = self._get_submission(obj)
        if submission is None:
            return "not_started"
        return submission.status

    def get_progress_percentage(self, obj) -> float:
        submission = self._get_submission(obj)

        if submission is None:
            return 0.00

        total_required = obj.survey.questions.filter(is_required=True).count()
        if total_required == 0:
            return 100.00

        answered = submission.answers.filter(question__is_required=True).count()
        return round((answered / total_required) * 100, 1)

    def get_unanswered_required_count(self, obj) -> int:
        submission = self._get_submission(obj)
        total_required = obj.survey.questions.filter(is_required=True).count()

        if submission is None:
            return total_required

        answered = submission.answers.filter(question__is_required=True).count()
        return total_required - answered

    def get_started_at(self, obj) -> datetime | None:
        submission = self._get_submission(obj)
        return submission.started_at if submission is not None else None

    def get_finished_at(self, obj) -> datetime | None:
        submission = self._get_submission(obj)
        return submission.finished_at if submission is not None else None


class AnswerDict(TypedDict):
    id: UUID
    option_text: str | None
    answered_at: datetime


class QuestionProgressSerializer(serializers.ModelSerializer):
    answered = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "text", "order", "is_required", "answered", "answer"]

    def get_answered(self, obj) -> bool:
        answers = self.context.get("answers", [])
        return any(a.question_id == obj.id for a in answers)

    def get_answer(self, obj) -> AnswerDict | None:
        answers = self.context.get("answers", [])
        answer = next((a for a in answers if a.question_id == obj.id), None)

        if answer is None:
            return None

        return {
            "id": str(answer.id),
            "option_text": answer.option.text if answer.option else None,
            "answered_at": answer.answered_at,
        }


class QuestionProgressDict(TypedDict):
    id: UUID
    text: str
    order: int
    is_required: bool
    answered: bool
    answer: AnswerDict | None


class RespondentProgressDetailSerializer(RespondentProgressListSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(RespondentProgressListSerializer.Meta):
        fields = [
            *RespondentProgressListSerializer.Meta.fields,
            "questions",
        ]

    def get_questions(self, obj) -> list[QuestionProgressDict]:
        submission = self._get_submission(obj)
        answers = list(submission.answers.all()) if submission else []

        questions = obj.survey.questions.order_by("order")

        return QuestionProgressSerializer(
            questions,
            many=True,
            context={"answers": answers},
        ).data
