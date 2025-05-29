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


@pytest.fixture(name="unauthenticated_client")
def fixture_unauthenticated_client():
    """ Fixture providing unauthenticated client """
    return APIClient()


@pytest.fixture(name="authenticated_client")
def fixture_authenticated_client():
    """ Fixture that provides an authenticated API client. """
    client = APIClient()
    User.objects.create_user(username="testuser", password="testpass123")
    credentials = base64.b64encode(b"testuser:testpass123").decode("ascii")
    client.credentials(HTTP_AUTHORIZATION=f"Basic {credentials}")
    return client


@pytest.fixture(name="test_conversations")
def fixture_sample_conversations():
    """Fixture to create sample conversations for testing"""
    return [
        Conversation.objects.create(
            diet_type=Conversation.DietType.VEGAN,
            favorite_foods=["tofu", "kale", "lentils"]
        ),
        Conversation.objects.create(
            diet_type=Conversation.DietType.VEGETARIAN,
            favorite_foods=["cheese", "mushrooms", "avocado"]
        ),
        Conversation.objects.create(
            diet_type=Conversation.DietType.OMNIVORE,
            favorite_foods=["steak", "chicken", "eggs"]
        )
    ]


@pytest.mark.django_db
@pytest.mark.parametrize("client_fixture, expected_status", [
    ("authenticated_client", status.HTTP_200_OK),
    ("unauthenticated_client", status.HTTP_401_UNAUTHORIZED),
])
def test_authentication_requirements(
    request,  # pytest request fixture
    client_fixture,
    expected_status,
):
    """ Test authentication requirements """
    client = request.getfixturevalue(client_fixture)
    url = reverse("conversation-insights")
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize("diet_query_param, expected_result_count, expected_diets", [
    ("vegan,vegetarian", 2, ["vegan", "vegetarian"]),
    ("vegetarian", 1, ["vegetarian"]),
    ("omnivore", 1, ["omnivore"]),
    ("vegan,vegetarian,omnivore", 3, ["vegan", "vegetarian", "omnivore"]),
])
def test_get_conversations_with_diet_filters(
    authenticated_client,
    test_conversations,  # pylint: disable=unused-argument
    diet_query_param,
    expected_result_count,
    expected_diets,
):
    """ Test various diet filter combinations """
    url = reverse("conversation-insights") + f"?diet={diet_query_param}"
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == expected_result_count
    assert all(result["diet_type"] in expected_diets for result in results)


@pytest.mark.django_db
@pytest.mark.parametrize("query_param, expected_result_count", [
    ("", 3),        # No param
    ("?diet=", 3),  # Empty param
    ("?diet", 3),   # Malformed param
])
def test_get_conversations_with_empty_params(
    authenticated_client,
    test_conversations,  # pylint: disable=unused-argument
    query_param,
    expected_result_count,
):
    """ Test edge cases with empty or missing query params """
    url = reverse("conversation-insights") + query_param
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == expected_result_count


@pytest.mark.django_db
@pytest.mark.parametrize("invalid_param", [
    "carnivore",
    "vegan,invalid",
    "123",
    "vegetarian,vegan,invalid",
])
def test_invalid_diet_params(authenticated_client, invalid_param, caplog):
    """ Test handling of invalid diet parameters """
    url = reverse("conversation-insights") + f"?diet={invalid_param}"
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid diet types" in response.json().get("error", "")
    assert any(record.levelname == "WARNING" for record in caplog.records)
