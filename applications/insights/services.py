""" Module to carry the insights app's business logic. """
from django.db.models import QuerySet

from applications.surveys.models import Conversation


def get_conversations_by_diet(diet_filters: list[str]) -> QuerySet[Conversation]:
    """ Returns a queryset of conversations filtered by diet types. """
    return Conversation.objects.filter(diet_type__in=diet_filters).order_by("-created_at")
