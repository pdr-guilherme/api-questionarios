from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.answers.api.serializers.answer import AnswerSerializer
from apps.answers.models import Submission, SurveyAccess
from apps.surveys.models import Survey


class SubmissionListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    survey_title = serializers.CharField(source="survey.title", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "survey",
            "survey_title",
            "status",
            "started_at",
            "finished_at",
            "user",
        ]
        read_only_fields = [
            "id",
            "status",
            "started_at",
            "finished_at",
        ]

    def validate_survey(self, survey):
        user = self.context["request"].user

        if survey.status != Survey.StatusChoices.PUBLISHED:
            msg = (
                "Não é possível iniciar um preenchimento "
                "de um questionário não publicado."
            )
            raise serializers.ValidationError(_(msg))

        if not SurveyAccess.objects.filter(survey=survey, user=user).exists():
            raise serializers.ValidationError(
                _("Você não tem acesso a esse questionário.")
            )

        return survey


class SubmissionDetailSerializer(SubmissionListSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta(SubmissionListSerializer.Meta):
        fields = [
            *SubmissionListSerializer.Meta.fields,
            "created_at",
            "updated_at",
            "answers",
        ]
