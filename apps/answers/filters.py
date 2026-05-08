import django_filters

from apps.answers.models import Submission


class AdminSubmissionFilter(django_filters.FilterSet):
    survey = django_filters.UUIDFilter(field_name="survey__id")
    user = django_filters.UUIDFilter(field_name="user__id")
    status = django_filters.ChoiceFilter(choices=Submission.StatusChoices.choices)
    started_after = django_filters.DateFilter(
        field_name="started_at", lookup_expr="gte"
    )
    started_before = django_filters.DateFilter(
        field_name="started_at", lookup_expr="lte"
    )

    class Meta:
        model = Submission
        fields = ["survey", "user", "status", "started_after", "started_before"]
