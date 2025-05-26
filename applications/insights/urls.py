""" Urls that are specific to the insights app """
from django.urls import path

from applications.insights import views

urlpatterns = [
    path('insights', views.get_insights, name='insights'),
]
