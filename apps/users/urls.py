from django.urls import path

from apps.users.api.views import RespondentCreateView

app_name = "users"

urlpatterns = [
    path("respondents/", RespondentCreateView.as_view(), name="respondent_create"),
]
