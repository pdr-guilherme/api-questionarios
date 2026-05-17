from rest_framework import serializers

from apps.answers.models import Answer, Submission


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
