""" Module to carry the insights app's specific configuration; aligns with Django's app isolation best practices. """
from django.apps import AppConfig


class InsightsConfig(AppConfig):
    """ Explicit AppConfig for insights app"""
    name = 'applications.insights'
    label = 'insights'
    verbose_name = "Insights"
