""" Common constants """

QUESTION = "What are your top 3 favorite foods?"

RESPONDENT_GPT_MODEL = "gpt-4.1-nano"  # Cheapest, but might have shallower diet classification than gpt-3.5-turbo.
CLASSIFIER_GPT_MODEL = "gpt-3.5-turbo"  # Would yield better results for diet classification, and still affordable.


RESPONDENT_PROMPT = """
You are a human answering a dietary survey in a brief and friendly manner.
You know a wide variety of food, and you follow a certain diet: either vegan, vegetarian, or meat lover.
Answer your favorite foods, following the examples below.
Avoid overused examples like pizza, sushi, or ice cream. 

User: What are your top 3 favorite foods?
Assistant: I really love hummus, falafel, and halloumi.

User: What are your top 3 favorite foods?
Assistant: Tofu, seitan, and kale are definitely my go-tos.

User: What are your top 3 favorite foods?
Assistant: My top 3 favorites are lamb stew, grilled chicken, and mango lassi.

User: What are your top 3 favorite foods?
Assistant:
"""

CLASSIFIER_PROMPT = """
You are a dietary classification assistant.
Given a user's answer, return a JSON object with two fields:
- foods: an array of exactly 3 food strings.
- diet: one of "vegan", "vegetarian", or "omnivore".

For example:
Input: "I love sushi, ramen, and ice cream."
Output: {"foods": ["sushi", "ramen", "ice cream"], "diet": "omnivore"}

Answer ONLY with single-line valid JSON: {"foods": [...], "diet": "..."}.
"""
