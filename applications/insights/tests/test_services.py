""" Unit tests for insights/services.py """
# pylint: disable=missing-function-docstring
import pytest
from django.utils import timezone
from applications.surveys.models import Conversation
from applications.insights.services import get_conversations_by_diet


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
