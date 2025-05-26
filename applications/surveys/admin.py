""" Module to register the survey apps' models in admin sites. """
from django.contrib import admin

from applications.surveys.models import Conversation


admin.site.register(Conversation)
