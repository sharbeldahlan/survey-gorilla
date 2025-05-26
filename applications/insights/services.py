""" Module to carry the insights app's business logic. """
from django.db.models import QuerySet

from applications.surveys.models import Conversation


VALID_DIETS = {diet for diet, _ in Conversation.DietType.choices}


def parse_diet_query_param(param: str | None) -> list[str]:
    """ Parses and validates the 'diet' query parameter. """
    if not param:
        return []

    diet_filters = [diet.strip() for diet in param.split(",") if diet.strip()]

    invalid = [d for d in diet_filters if d not in VALID_DIETS]
    if invalid:
        raise ValueError(f"Invalid diet types in query: {', '.join(invalid)}")

    return diet_filters


def get_conversations_by_diet(diet_filters: list[str]) -> QuerySet[Conversation]:
    """ Returns a queryset of conversations filtered by diet types. """
    return Conversation.objects.filter(diet_type__in=diet_filters).order_by("-created_at")
