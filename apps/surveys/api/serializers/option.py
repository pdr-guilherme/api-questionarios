from rest_framework import serializers

from apps.surveys.models import Option
from apps.surveys.utils import get_next_order


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = "__all__"
        read_only_fields = ["id", "question"]

    def create(self, validated_data):
        if validated_data.get("order") is None:
            question = validated_data["question"]
            next_order = get_next_order(Option, question=question)
            validated_data["order"] = next_order

        return super().create(validated_data)
