""" Module to register the survey apps' models in admin sites. """
from django.contrib import admin

from applications.surveys.models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """ Table view for Conversation model in the admin page. """
    list_display = ("id", "answer_text", "favorite_foods", "diet_type", "created_at")
    search_fields = ("answer_text", "favorite_foods")
    list_filter = ("diet_type", "created_at")
    ordering = ("-created_at",)
