from django.contrib import admin

from apps.surveys.models import Option, Question, QuestionImage, Survey

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(QuestionImage)
admin.site.register(Option)
