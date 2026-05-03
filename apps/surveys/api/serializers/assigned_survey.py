from rest_framework import serializers

from apps.answers.models import Submission
from apps.surveys.api.serializers.question import QuestionDetailSerializer
from apps.surveys.models import Survey, User


class AssignedSurveySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        exclude = ["respondents", "status"]

    def get_completed(self, obj) -> bool:
        user = self.context["request"].user

        return any(
            submission.user_id == user.id
            and submission.status == Submission.StatusChoices.COMPLETED
            for submission in obj.submissions.all()
        )


class AssignedSurveyDetailSerializer(AssignedSurveySerializer):
    questions = QuestionDetailSerializer(many=True, read_only=True)

    class Meta(AssignedSurveySerializer.Meta):
        exclude = [*AssignedSurveySerializer.Meta.exclude]


class GrantAccessSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

    def validate_user_id(self, value):
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Usuário não encontrado.")
        return value
