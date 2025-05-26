""" Module to carry the survey app's business logic. """
from openai import OpenAI
from django.conf import settings

from applications.constants import (
    GPT_MODEL,
    QUESTION_PROMPT,
)
from applications.surveys.models import Conversation


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ask_question(question: str, gpt_model: str) -> str:
    """
    Ask a question and return its raw answer text.
    """
    resp = client.chat.completions.create(
        model=gpt_model,
        messages=[{"role": "user", "content": question}],
        temperature=0.8,
        top_p=1.0,
    )
    content = resp.choices[0].message.content
    return content.strip() if content else ""


def simulate_conversation() -> None:
    """ Ask the question, and store the raw answer (along with the question) to the Conversation table. """
    answer = ask_question(question=QUESTION_PROMPT, gpt_model=GPT_MODEL)

    Conversation.objects.create(
        question_text=QUESTION_PROMPT,
        answer_text=answer
    )
