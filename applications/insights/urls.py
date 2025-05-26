""" URL configuration for the insights application. """
from django.urls import path

from applications.insights.views import ConversationInsightsView

urlpatterns = [
    path('insights/conversations', ConversationInsightsView.as_view(), name='conversation-insights'),
]
