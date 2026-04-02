from rest_framework import serializers

from surveys.models import Survey


class SurveySerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Survey
        fields = "__all__"
