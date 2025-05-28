""" Module to carry the survey app's business logic. """
import json

from openai import OpenAI
from django.conf import settings

from applications.constants import (
    CLASSIFIER_GPT_MODEL,
    CLASSIFIER_PROMPT,
    QUESTION,
    RESPONDENT_GPT_MODEL,
    RESPONDENT_PROMPT,
)
from applications.logging import get_logger
from applications.surveys.models import Conversation


client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = get_logger(__name__)


def ask_question(respondent_gpt_model: str, respondent_prompt: str, question: str) -> str:
    """
    Ask a question and return its raw answer text.

    Params:
      - respondent_gpt_model (str): The GPT model responding. This is any GPT model available from OpenAI.
      - respondent_prompt (str): The system prompt sent to the respondent GPT to guide it to respond naturally
          and randomize answers.
      - question (str): Survey conductor's question.

    Return:
      - A string containing respondent's answer.
    """
    resp = client.chat.completions.create(
        model=respondent_gpt_model,
        messages=[
            {"role": "system", "content": respondent_prompt},
            {"role": "user", "content": question},
        ],
        temperature=1.2,
        timeout=30,
    )
    content = resp.choices[0].message.content
    return content.strip() if content else ""


def classify_diet(classifier_gpt_model: str, classifier_prompt: str,  answer: str) -> dict:
    """
    Classify the diet and extract foods from an answer via ChatGPT. Includes parsing and validation.

    Params:
      - classifier_gpt_model (str): The GPT model for classifying diets.
      - classifier_prompt (str): The system prompt sent to the classifier GPT to guide it to classify the diet
          from the text answer and to return a JSON object with the parsed list of foods and the diet.
      - answer (str): Respondent's text answer containing favorite foods.

    Validation:
      - Raises ValueError for any unexpected response format.
      - Raises ValueError if diet classification is invalid (unsupported in our system).

    Return:
      - A dict with keys 'foods' (list[str]) and 'diet' (str).


    Example:
      - answer: "I love sushi, ramen, and ice cream."
      - output: {"foods": ["sushi", "ramen", "ice cream"], "diet": "omnivore"}
    """
    resp = client.chat.completions.create(
        model=classifier_gpt_model,
        messages=[
            {"role": "system", "content": classifier_prompt},
            {"role": "user", "content": answer},
        ],
        temperature=0,
    )
    content = resp.choices[0].message.content
    if not content:
        raise ValueError("Empty response from GPT")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON from GPT: {content}", content, e.pos)

    # Validate structure
    foods = parsed.get("foods")
    diet = parsed.get("diet")

    if not isinstance(foods, list) or len(foods) != 3 or not all(isinstance(f, str) for f in foods):
        raise ValueError(f"Invalid 'foods' format: {foods}")

    if diet not in {
        Conversation.DietType.VEGAN,
        Conversation.DietType.VEGETARIAN,
        Conversation.DietType.OMNIVORE,
    }:
        raise ValueError(f"Invalid diet classification: {diet}")

    return {"foods": foods, "diet": diet}


def simulate_conversation() -> None:
    """
    Simulate and process a single food preference conversation between two chatbots:
      - Survey conductor bot asking a respondent bot a standard question, simulating a real-life survey question.
      - Respondent bot answers something "random" to simulate a real life survey respondent.
      - Survey conductor takes the answer and classifies the diet of respondent,
          simulating insight extraction from the survey.

    Performs these operations in sequence:
      - Generates a randomized answer to the food preference question.
      - Creates a base Conversation record with the raw answer.
      - Attempts to classify the diet type and extract food items.
      - Updates the record with classification results if successful.
      - Logs the failure and conversation ID if not successful.
    """
    answer = ask_question(
        respondent_gpt_model=RESPONDENT_GPT_MODEL,
        respondent_prompt=RESPONDENT_PROMPT,
        question=QUESTION,
    )

    conversation = Conversation.objects.create(
        question_text=QUESTION,
        answer_text=answer,
    )

    try:
        result = classify_diet(
            classifier_gpt_model=CLASSIFIER_GPT_MODEL,
            classifier_prompt=CLASSIFIER_PROMPT,
            answer=answer,
        )
        conversation.favorite_foods = result["foods"]
        conversation.diet_type = result["diet"]
        conversation.save()
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("Classification failed for conversation ID %s: %s", conversation.id, e)
