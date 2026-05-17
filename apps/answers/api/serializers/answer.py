from rest_framework import serializers

from apps.answers.models import Answer


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
