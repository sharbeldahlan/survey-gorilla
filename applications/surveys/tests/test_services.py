""" Unit tests for surveys/services.py """
from unittest.mock import MagicMock

import pytest
from applications.surveys.models import Conversation
from applications.surveys.services import (
    ask_question,
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
    assert type(text) is str


@pytest.mark.django_db
def test_simulate_conversation__creates_conversations(monkeypatch):
    """ Happy path test """
    # Arrange
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [
        MagicMock(choices=[
            MagicMock(message=MagicMock(content="I love pizza, sushi, and salad."))
        ]),
    ]
    monkeypatch.setattr("applications.surveys.services.client", mock_client)

    # Act
    simulate_conversation()

    # Assert the database was created and populated correctly
    conversation = Conversation.objects.first()
    assert "foods?" in conversation.question_text
    assert conversation.answer_text == "I love pizza, sushi, and salad."
    assert conversation.favorite_foods == []
    assert conversation.diet_type is None
