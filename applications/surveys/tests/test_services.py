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


@pytest.fixture(name="mock_openai")
def fixture_mock_openai(monkeypatch):
    """ Fixture to patch OpenAI client and return controllable responses. """
    mock_client = MagicMock()
    monkeypatch.setattr('applications.surveys.services.client', mock_client)
    return mock_client


@pytest.mark.django_db
def test_ask_question__returns_text(mock_openai):
    """ Trivial test case for mocked simple ChatGPT prompt. """
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="growl"))]
    )
    text = ask_question("mock model", "act like an animal",  "hey gorilla!")
    assert text == "growl"
    assert isinstance(text, str)


@pytest.mark.django_db
def test_classify_diet__parses_json(mock_openai):
    """ Test that classify_diet function correctly returns a dict with keys 'foods' (list[str]) and 'diet' (str). """
    mock_json = '{"foods": ["tofu", "lentils", "kale"], "diet": "vegan"}'
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=mock_json))]
    )

    result = classify_diet("mock model", "mock prompt", "mock answer")
    assert result["foods"] == ["tofu", "lentils", "kale"]
    assert result["diet"] == Conversation.DietType.VEGAN


@pytest.mark.django_db
def test_classify_diet__raises_on_invalid_json(mock_openai):
    """ Test that classify_diet propagates JSON errors. """
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="INVALID JSON"))]
    )

    with pytest.raises(json.JSONDecodeError):
        classify_diet("mock model", "mock prompt", "bad answer")


@pytest.mark.django_db
def test_classify_diet__raises_on_invalid_structure(mock_openai):
    """ Should raise ValueError for valid JSON with wrong structure """
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(
            content='{"foods": ["kale"], "diet": "vegetarian"}'
        ))]
    )

    with pytest.raises(ValueError, match="Invalid 'foods' format"):
        classify_diet("mock model", "mock prompt", "mock answer")


@pytest.mark.django_db
def test_classify_diet__raises_on_invalid_diet(mock_openai):
    """ Should raise ValueError for unknown diet """
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(
            content='{"foods": ["apple", "banana", "kale"], "diet": "meatitarian"}'
        ))]
    )

    with pytest.raises(ValueError, match="Invalid diet classification"):
        classify_diet("mock model", "mock prompt", "mock answer")


@pytest.mark.django_db
def test_simulate_conversation__creates_conversations(mock_openai):
    """ Happy path test """
    # Arrange
    mock_openai.chat.completions.create.side_effect = [
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

    # Act: run the service
    simulate_conversation()

    # Assert the database was created and populated correctly
    conversation = Conversation.objects.first()
    assert "foods?" in conversation.question_text
    assert conversation.answer_text == "I love pizza, sushi, and salad."
    assert conversation.favorite_foods == ["pizza", "sushi", "salad"]
    assert conversation.diet_type == Conversation.DietType.OMNIVORE


@pytest.mark.django_db
def test_simulate_conversation__handles_bad_json(mock_openai, caplog):
    """ Test simulate_conversation handles malformed JSON gracefully (does not write to database). """
    mock_answer = "I love everything."
    mock_openai.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=MagicMock(content=mock_answer))]),
        MagicMock(choices=[MagicMock(message=MagicMock(content="NOT_JSON"))])
    ]

    simulate_conversation()

    conversation = Conversation.objects.first()
    # favorite_foods should remain default empty list and diet_type None
    assert conversation.favorite_foods == []
    assert conversation.diet_type is None
    assert any(
        "Classification failed for conversation ID" in record.message
        for record in caplog.records
    )
    assert any(record.levelname == "WARNING" for record in caplog.records)
