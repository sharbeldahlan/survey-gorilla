""" Module to carry the models of the surveys app. """
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    """
    Model to store the conversations carried out by AI chatbots.

    Currently, the fields storing insights extracted from the conversation are also in this model for the sake
    of simplicity, since it helps understand the full picture of the conversation. In the future, there might
    be need to have separate models that store raw data than the ones that store extracted insights.
    """
    class DietType(models.TextChoices):
        """
        DietType choices are currently kept simple;
        with 'vegan' being most strict and 'omnivore' encompassing no restrictions.
        """
        VEGAN = 'vegan', _('Vegan')
        VEGETARIAN = 'vegetarian', _('Vegetarian')
        OMNIVORE = 'omnivore', _('Omnivore')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_text = models.TextField()
    answer_text = models.TextField()
    favorite_foods = models.JSONField(default=list, null=True, blank=True)
    diet_type = models.CharField(max_length=20, choices=DietType, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_veg(self):
        """ Util that helps filtering objects based on a vegetarian/vegan diet. """
        return self.diet_type in {
            self.DietType.VEGETARIAN,
            self.DietType.VEGAN,
        }
