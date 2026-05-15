from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.answers.models import Answer, Submission, SurveyAccess
from apps.surveys.models import Survey


class SubmissionListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    survey_title = serializers.CharField(source="survey.title", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "survey",
            "survey_title",
            "status",
            "started_at",
            "finished_at",
            "user",
        ]
        read_only_fields = [
            "id",
            "status",
            "started_at",
            "finished_at",
        ]

    def validate_survey(self, survey):
        user = self.context["request"].user

        if survey.status != Survey.StatusChoices.PUBLISHED:
            msg = (
                "Não é possível iniciar um preenchimento "
                "de um questionário não publicado."
            )
            raise serializers.ValidationError(_(msg))

        if not SurveyAccess.objects.filter(survey=survey, user=user).exists():
            raise serializers.ValidationError(
                _("Você não tem acesso a esse questionário.")
            )

        return survey


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)
    option_text = serializers.CharField(source="option.text", read_only=True)

    class Meta:
        model = Answer
        fields = [
            "id",
            "submission",
            "question",
            "question_text",
            "option",
            "option_text",
            "answered_at",
        ]
        read_only_fields = ["id", "submission"]


class SubmissionDetailSerializer(SubmissionListSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta(SubmissionListSerializer.Meta):
        fields = [
            *SubmissionListSerializer.Meta.fields,
            "created_at",
            "updated_at",
            "answers",
        ]


class AdminSubmissionListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    survey_title = serializers.CharField(source="survey.title", read_only=True)
    answers_count = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            "id",
            "user_email",
            "survey_title",
            "status",
            "started_at",
            "finished_at",
            "answers_count",
        ]

    def get_answers_count(self, obj) -> int:
        return obj.answers.count()


class AdminAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)
    question_order = serializers.IntegerField(source="question.order", read_only=True)
    option_text = serializers.CharField(source="option.text", read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "question_text", "question_order", "option_text", "answered_at"]


class AdminSubmissionDetailSerializer(AdminSubmissionListSerializer):
    answers = AdminAnswerSerializer(many=True, read_only=True)

    class Meta(AdminSubmissionListSerializer.Meta):
        fields = [
            *AdminSubmissionListSerializer.Meta.fields,
            "answers",
        ]
