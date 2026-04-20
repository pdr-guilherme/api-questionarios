from rest_framework import serializers

from apps.surveys.models import Option, Question, QuestionImage, Survey
from apps.surveys.utils import get_next_order
from apps.users.models import User


class SurveySerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Survey
        fields = "__all__"


class AssignedSurveySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Survey
        exclude = ["respondents", "status"]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        if validated_data.get("order") is None:
            survey = validated_data["survey"]
            next_order = get_next_order(Question, survey=survey)
            validated_data["order"] = next_order

        return super().create(validated_data)


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


# used for detail views
class QuestionDetailSerializer(serializers.ModelSerializer):
    images = QuestionImageSerializer(many=True, required=False)
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ["id"]

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


class GrantAccessSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

    def validate_user_id(self, value):
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Usuário não encontrado.")
        return value
