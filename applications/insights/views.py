"""
The views module of the insights application.
Defines API endpoints for querying insights from survey conversations.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from applications.insights.serializers import ConversationInsightSerializer
from applications.insights.services import (
    get_conversations_by_diet,
    parse_diet_query_param,
)


class ConversationInsightsView(APIView):
    """
    API endpoint that returns conversations filtered by diet type.

    Query Parameters:
        diet (str): Comma-separated list of diet types to include. Valid values:
            "vegan", "vegetarian", "omnivore".
            Example: ?diet=vegetarian,vegan

    Returns:
        200 OK: List of serialized Conversation objects matching the filter.
        400 Bad Request: If any provided diet type is invalid.
    """
    def get(self, request):
        # pylint: disable=missing-function-docstring
        diet_param = request.query_params.get("diet", "")

        try:
            diet_list = parse_diet_query_param(diet_param)
        except ValueError as e:
            return Response({"error_message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        conversations = get_conversations_by_diet(diet_list)
        serializer = ConversationInsightSerializer(conversations, many=True)
        return Response(serializer.data)
