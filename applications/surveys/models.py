import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    class DietType(models.TextChoices):
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
        return self.diet_type in {
            self.DietType.VEGETARIAN,
            self.DietType.VEGAN,
        }
