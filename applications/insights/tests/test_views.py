"""
Tests for insights/views.py
These are more like end-to-end since they test logic of the models, serializers, views, and services.
"""
import base64

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.urls import reverse

from applications.surveys.models import Conversation


@pytest.fixture(name="authenticated_client")
def fixture_authenticated_client():
    """ Fixture that provides an authenticated API client. """
    client = APIClient()
    User.objects.create_user(username="testuser", password="testpass123")
    credentials = base64.b64encode(b"testuser:testpass123").decode("ascii")
    client.credentials(HTTP_AUTHORIZATION=f"Basic {credentials}")
    return client


@pytest.mark.django_db
def test_unauthenticated_access_fails():
    """ Test that unauthenticated requests get 401 response. """
    client = APIClient()
    url = reverse("conversation-insights")
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_invalid_credentials_fail():
    """ Test that invalid credentials get 401 response. """
    client = APIClient()
    credentials = base64.b64encode(b"wronguser:wrongpass").decode("ascii")
    client.credentials(HTTP_AUTHORIZATION=f"Basic {credentials}")
    url = reverse("conversation-insights")
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_conversations__filtered_by_valid_diets(authenticated_client):
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

    url = reverse("conversation-insights") + "?diet=vegan,vegetarian"
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 2
    assert all(r["diet_type"] in ["vegan", "vegetarian"] for r in results)


@pytest.mark.django_db
def test_get_conversations__empty_diet_param__returns_all(authenticated_client):
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

    url = reverse("conversation-insights") + "?diet="  # Query param available but empty
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 3


@pytest.mark.django_db
def test_get_conversations__no_query_param__returns_all(authenticated_client):
    """ Simulate the GET endpoint when no query params given. """
    Conversation.objects.create(
        diet_type=Conversation.DietType.VEGAN,
        favorite_foods=["tofu", "kale", "lentils"]
    )

    url = reverse("conversation-insights")  # No query param
    response = authenticated_client.get(url)
    results = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(results) == 1


@pytest.mark.django_db
def test_get_conversations__invalid_diet_param(authenticated_client, caplog):
    """ Simulate when filtered by invalid diet params """
    url = reverse("conversation-insights") + "?diet=carnivore"
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Inspect and test the actual error payload
    error_data = response.json()
    assert any("Invalid diet types" in msg for msg in error_data.values())
    assert any(
        "Invalid diet filter" in record.message
        for record in caplog.records
    )
    assert any(record.levelname == "WARNING" for record in caplog.records)
