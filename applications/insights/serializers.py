"""
Serializers for the insights application.
Provides presentation logic for Conversation models.
"""
from rest_framework import serializers
from applications.surveys.models import Conversation


class ConversationInsightSerializer(serializers.ModelSerializer):
    """
    Serializes a Conversation instance for dietary insights API.
    Excludes raw conversation fields.
    """
    class Meta:
        # pylint: disable=missing-class-docstring, too-few-public-methods
        model = Conversation
        fields = ["id", "diet_type", "favorite_foods", "created_at"]
