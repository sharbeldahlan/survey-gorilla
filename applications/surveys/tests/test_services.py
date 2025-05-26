""" Unit tests for surveys/services.py """
import json
from unittest.mock import MagicMock

import pytest
from applications.surveys.models import Conversation
from applications.surveys.services import (
    ask_question,
    classify_diet,
    simulate_conversation,
)


@pytest.mark.django_db
def test_ask_question__returns_text(monkeypatch):
    """ Trivial test case for mocked simple ChatGPT prompt. """
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="growl"))]
    )
    monkeypatch.setattr('applications.surveys.services.client', mock_client)

    text = ask_question("hey gorilla!", 'mock model')
    assert text == "growl"
    assert isinstance(text, str)


@pytest.mark.django_db
def test_classify_diet__parses_json(monkeypatch):
    """ Test that classify_diet function correctly returns a dict with keys 'foods' (list[str]) and 'diet' (str). """
    mock_answer = "irrelevant"
    mock_json = '{"foods": ["tofu", "lentils", "kale"], "diet": "vegan"}'
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=mock_json))]
    )
    monkeypatch.setattr('applications.surveys.services.client', mock_client)

    result = classify_diet(mock_answer, 'mock prompt', 'mock model')
    assert result["foods"] == ["tofu", "lentils", "kale"]
    assert result["diet"] == Conversation.DietType.VEGAN


@pytest.mark.django_db
def test_classify_diet__raises_on_invalid_json(monkeypatch):
    """ Test that classify_diet propagates JSON errors. """
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="INVALID JSON"))]
    )
    monkeypatch.setattr('applications.surveys.services.client', mock_client)

    with pytest.raises(json.JSONDecodeError):
        classify_diet("bad answer", 'mock prompt', 'mock model')


@pytest.mark.django_db
def test_simulate_conversation__creates_conversations(monkeypatch):
    """ Happy path test """
    # Arrange
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [
        # First response (food answer)
        MagicMock(choices=[
            MagicMock(message=MagicMock(content="I love pizza, sushi, and salad."))
        ]),
        # Second response (classification)
        MagicMock(choices=[
            MagicMock(message=MagicMock(
                content='{"foods": ["pizza", "sushi", "salad"], "diet": "omnivore"}'
            ))
        ])
    ]
    monkeypatch.setattr("applications.surveys.services.client", mock_client)

    # Act: run the service
    simulate_conversation()

    # Assert the database was created and populated correctly
    conversation = Conversation.objects.first()
    assert "foods?" in conversation.question_text
    assert conversation.answer_text == "I love pizza, sushi, and salad."
    assert conversation.favorite_foods == ["pizza", "sushi", "salad"]
    assert conversation.diet_type == Conversation.DietType.OMNIVORE
