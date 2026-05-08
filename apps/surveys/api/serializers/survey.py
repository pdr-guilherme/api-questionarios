from rest_framework import serializers

from apps.surveys.api.serializers.question import QuestionDetailSerializer
from apps.surveys.models import Survey


class SurveySerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    respondents = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Survey
        fields = "__all__"


class SurveyDetailSerializer(SurveySerializer):
    questions = QuestionDetailSerializer(many=True, read_only=True)

    class Meta(SurveySerializer.Meta):
        fields = "__all__"
