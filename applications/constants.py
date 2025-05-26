""" Common constants """

RANDOMIZER_GPT_MODEL = "gpt-4.1-nano"  # Cheapest, but might have shallower diet classification than gpt-3.5-turbo.
CLASSIFIER_GPT_MODEL = "gpt-3.5-turbo"  # Would yield better results for diet classification, and still affordable.

QUESTION_PROMPT = "What are your top 3 favorite foods?"

CLASSIFY_PROMPT = """
You are a dietary classification assistant.
Given a user’s answer, return a JSON object with two fields:
- foods: an array of exactly 3 food strings.
- diet: one of "vegan", "vegetarian", or "omnivore".

For example:
Input: "I love sushi, ramen, and ice cream."
Output: {"foods": ["sushi", "ramen", "ice cream"], "diet": "omnivore"}

Answer only with the JSON.
"""
