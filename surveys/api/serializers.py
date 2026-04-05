from django.db.models import Max
from rest_framework import serializers

from surveys.models import Option, Question, QuestionImage, Survey


class SurveySerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Survey
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        if validated_data.get("order") is None:
            survey = validated_data["survey"]

            last_order = Question.objects.filter(survey=survey).aggregate(Max("order"))[
                "order__max"
            ]

            validated_data["order"] = (last_order or 0) + 1

        return super().create(validated_data)


class QuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = "__all__"
        read_only_fields = ["id", "uploaded_at", "question"]

    def create(self, validated_data):
        if validated_data.get("order") is None:
            question = validated_data["question"]

            last_order = QuestionImage.objects.filter(question=question).aggregate(
                Max("order")
            )["order__max"]

            validated_data["order"] = (last_order or 0) + 1

        return super().create(validated_data)


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = "__all__"
        read_only_fields = ["id", "question"]

    def create(self, validated_data):
        if validated_data.get("order") is None:
            question = validated_data["question"]

            last_order = Option.objects.filter(question=question).aggregate(
                Max("order")
            )["order__max"]

            validated_data["order"] = (last_order or 0) + 1

        return super().create(validated_data)


# used for detail views
class QuestionDetailSerializer(serializers.ModelSerializer):
    images = QuestionImageSerializer(many=True)

    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ["id"]

    def create(self, validated_data):
        images_data = validated_data.pop("images")
        question = Question.objects.create(**validated_data)

        for image_data in images_data:
            serializer = QuestionImageSerializer(data=image_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(question=question)

        return question
