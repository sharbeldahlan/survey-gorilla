""" The main API view. """
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def get_insights(request):
    if request.method == 'GET':
        return Response({'message': 'Here are your insights!'}, status=status.HTTP_200_OK)
