from rest_framework import serializers

from apps.surveys.api.serializers.option import OptionSerializer
from apps.surveys.api.serializers.question_image import QuestionImageSerializer
from apps.surveys.models import Question
from apps.surveys.utils import get_next_order


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text", "order", "is_required", "survey"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        if validated_data.get("order") is None:
            survey = validated_data["survey"]
            next_order = get_next_order(Question, survey=survey)
            validated_data["order"] = next_order

        return super().create(validated_data)


class QuestionDetailSerializer(serializers.ModelSerializer):
    images = QuestionImageSerializer(many=True, required=False)
    options = OptionSerializer(many=True, required=False)

    class Meta(QuestionSerializer.Meta):
        fields = [*QuestionSerializer.Meta.fields, "images", "options"]

    def create(self, validated_data):
        images_data = validated_data.pop("images", None)
        options_data = validated_data.pop("options", None)
        question = Question.objects.create(**validated_data)

        if images_data is not None:
            for image_data in images_data:
                serializer = QuestionImageSerializer(data=image_data)
                serializer.is_valid(raise_exception=True)
                serializer.save(question=question)

        if options_data is not None:
            for option_data in options_data:
                serializer = OptionSerializer(data=option_data)
                serializer.is_valid(raise_exception=True)
                serializer.save(question=question)

        return question
