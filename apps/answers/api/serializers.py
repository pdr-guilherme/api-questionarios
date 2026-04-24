from rest_framework import serializers

from apps.answers.models import Answer, Submission


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
