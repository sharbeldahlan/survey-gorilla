from django.apps import AppConfig


class SurveysConfig(AppConfig):
    name = 'applications.surveys'
    label = 'surveys'
    verbose_name = "Survey Conversations"
    default_auto_field = 'django.db.models.BigAutoField'
