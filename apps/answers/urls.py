from django.urls import path

from apps.answers.api.views import answers_index

urlpatterns = [
    path("answers/", answers_index, name="index"),
]
