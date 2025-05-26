""" Module to carry the survey app's business logic. """
import json

from openai import OpenAI
from django.conf import settings

from applications.constants import (
    RANDOMIZER_GPT_MODEL,
    CLASSIFIER_GPT_MODEL,
    CLASSIFY_PROMPT,
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


def classify_diet(answer: str, prompt: str, gpt_model: str) -> dict:
    """
    Classify the diet and extract foods from an answer via ChatGPT.
    Returns a dict with keys 'foods' (list[str]) and 'diet' (str).
    """
    resp = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": answer}
        ],
        temperature=0,
    )
    content = resp.choices[0].message.content
    if not content:
        raise ValueError("Empty response from GPT")
    # Expecting a JSON string from the assistant
    return json.loads(content)


def simulate_conversation() -> None:
    """
    Simulate n conversations: ask the question, store raw answer,
    classify diet and parse foods, then update the Conversation record.
    """
    answer = ask_question(question=QUESTION_PROMPT, gpt_model=RANDOMIZER_GPT_MODEL)

    conversation = Conversation.objects.create(
        question_text=QUESTION_PROMPT,
        answer_text=answer
    )
    result = classify_diet(answer=answer, prompt=CLASSIFY_PROMPT, gpt_model=CLASSIFIER_GPT_MODEL)
    foods = result.get("foods")
    diet = result.get("diet")

    conversation.favorite_foods = foods
    conversation.diet_type = diet
    conversation.save()
