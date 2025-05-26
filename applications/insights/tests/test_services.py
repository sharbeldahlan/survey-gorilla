""" Unit tests for insights/services.py """
# pylint: disable=missing-function-docstring
import pytest
from django.utils import timezone
from applications.surveys.models import Conversation
from applications.insights.services import (
    get_conversations_by_diet,
    parse_diet_query_param,
)


def test_parse_diet_query_param__valid():
    result = parse_diet_query_param("vegan, vegetarian")
    assert sorted(result) == ["vegan", "vegetarian"]


def test_parse_diet_query_param__invalid():
    with pytest.raises(ValueError, match="Invalid diet types"):
        parse_diet_query_param("meatarian")


def test_parse_diet_query_param__empty():
    assert parse_diet_query_param("") == []


@pytest.mark.django_db
def test_get_conversations_by_diet():
    Conversation.objects.create(
        answer_text="Tofu, lentils, kale",
        diet_type=Conversation.DietType.VEGAN,
        favorite_foods=["tofu", "lentils", "kale"],
        created_at=timezone.now(),
    )
    results = get_conversations_by_diet(["vegan"])
    assert len(results) == 1
    assert results[0].diet_type == "vegan"
