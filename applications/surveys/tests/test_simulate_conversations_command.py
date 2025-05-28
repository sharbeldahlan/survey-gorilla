""" Tests for the simulate_conversations management command. """
from unittest.mock import patch, MagicMock

import pytest
from django.core.management import call_command
from openai import RateLimitError, APIError, APITimeoutError


@pytest.fixture(name="mock_simulate_conversation")
def fixture_mock_simulate_conversation():
    """ Fixture to patch simulate_conversation. """
    with patch("applications.surveys.management.commands.simulate_conversations.simulate_conversation") as mock:
        yield mock


@pytest.fixture(name="fake_request")
def fixture_fake_request():
    """ Fixture for a fake OpenAI request. """
    return MagicMock(name="FakeRequest")


@pytest.fixture(name="fake_response")
def fixture_fake_response(fake_request):
    """ Fixture for a fake OpenAI response. """
    mock_response = MagicMock(name="FakeResponse")
    mock_response.request = fake_request
    mock_response.headers = {}
    mock_response.status_code = 500
    return mock_response


@pytest.mark.django_db
def test_simulate_command_success(mock_simulate_conversation, capsys):
    """ Run simulate_conversation successfully 3 times. """
    call_command("simulate_conversations", "3")
    assert mock_simulate_conversation.call_count == 3
    output = capsys.readouterr().out
    assert "Finished simulations: 3 succeeded, 0 failed" in output


@pytest.mark.django_db
@pytest.mark.parametrize("exception", [
    RateLimitError("rate limit", response=MagicMock(), body=None),
    APIError("api error", request=MagicMock(), body=None),
    APITimeoutError(request=MagicMock())
])
def test_simulate_command_openai_failures(mock_simulate_conversation, capsys, exception):
    """ Handle OpenAI API-related failures. """
    mock_simulate_conversation.side_effect = exception
    call_command("simulate_conversations", "2")
    output = capsys.readouterr().out
    assert "Finished simulations: 0 succeeded, 2 failed" in output


@pytest.mark.django_db
def test_simulate_command_generic_failure(mock_simulate_conversation, capsys):
    """ Handle unexpected runtime errors. """
    mock_simulate_conversation.side_effect = RuntimeError("oops")
    call_command("simulate_conversations", "1")
    output = capsys.readouterr().out
    assert "Finished simulations: 0 succeeded, 1 failed" in output
