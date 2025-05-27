"""
Tests for insights/views.py
These are more like end-to-end since they test logic of the models, serializers, views, and services.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from applications.surveys.models import Conversation


@pytest.mark.django_db
def test_get_conversations__filtered_by_valid_diets():
    """ Simulate the GET endpoint when filtered by valid diets. """
    Conversation.objects.create(
        diet_type=Conversation.DietType.VEGAN,
        favorite_foods=["tofu", "kale", "lentils"]
    )
    Conversation.objects.create(
        diet_type=Conversation.DietType.VEGETARIAN,
        favorite_foods=["cheese", "mushrooms", "avocado"]
    )
    Conversation.objects.create(
        diet_type=Conversation.DietType.OMNIVORE,
        favorite_foods=["steak", "chicken", "eggs"]
    )

    client = APIClient()
    url = reverse("conversation-insights") + "?diet=vegan,vegetarian"
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 2
    assert all(r["diet_type"] in ["vegan", "vegetarian"] for r in results)


@pytest.mark.django_db
def test_get_conversations__empty_diet_param__returns_all():
    """ Simulate the GET endpoint when empty query params given like '?diet=' """
    Conversation.objects.create(
        diet_type=Conversation.DietType.VEGAN,
        favorite_foods=["tofu", "kale", "lentils"]
    )
    Conversation.objects.create(
        diet_type=Conversation.DietType.VEGETARIAN,
        favorite_foods=["cheese", "mushrooms", "avocado"]
    )
    Conversation.objects.create(
        diet_type=Conversation.DietType.OMNIVORE,
        favorite_foods=["steak", "chicken", "eggs"]
    )

    client = APIClient()
    url = reverse("conversation-insights") + "?diet="  # Query param available but empty
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 3
    assert all(r["diet_type"] in ["vegan", "vegetarian", "omnivore"] for r in results)


@pytest.mark.django_db
def test_get_conversations__no_query_param__returns_all():
    """ Simulate the GET endpoint when no query params given. """
    Conversation.objects.create(
        diet_type=Conversation.DietType.VEGAN,
        favorite_foods=["tofu", "kale", "lentils"]
    )

    client = APIClient()
    url = reverse("conversation-insights")  # No query param
    response = client.get(url)
    results = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(results) == 1


@pytest.mark.django_db
def test_get_conversations__invalid_diet_param(caplog):
    """ Simulate when filtered by invalid diet params """
    client = APIClient()
    url = reverse("conversation-insights") + "?diet=carnivore"
    response = client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Inspect and test the actual error payload
    error_data = response.json()
    assert any("Invalid diet types" in msg for msg in error_data.values())
    assert any(
        "Invalid diet filter" in record.message
        for record in caplog.records
    )
    assert any(record.levelname == "WARNING" for record in caplog.records)
