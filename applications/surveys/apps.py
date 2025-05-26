""" Module to carry the surveys app's specific configuration; aligns with Django's app isolation best practices. """
from django.apps import AppConfig


class SurveysConfig(AppConfig):
    """ Explicit AppConfig for surveys app"""
    name = 'applications.surveys'
    label = 'surveys'
    verbose_name = "Survey Conversations"
    default_auto_field = 'django.db.models.BigAutoField'
