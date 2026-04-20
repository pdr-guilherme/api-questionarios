from rest_framework import serializers

from apps.surveys.models import Survey


class SurveySerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Survey
        fields = "__all__"
