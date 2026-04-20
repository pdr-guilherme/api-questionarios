from rest_framework import serializers

from apps.surveys.models import QuestionImage
from apps.surveys.utils import get_next_order


class QuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = "__all__"
        read_only_fields = ["id", "uploaded_at", "question"]

    def create(self, validated_data):
        if validated_data.get("order") is None:
            question = validated_data["question"]
            next_order = get_next_order(QuestionImage, question=question)
            validated_data["order"] = next_order

        return super().create(validated_data)
