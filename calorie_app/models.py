from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django_filters import rest_framework as filters
from dj_rql.constants import FilterLookups
from dj_rql.filter_cls import RQLFilterClass
from dj_rql.constants import FilterLookups

User = get_user_model()
class FoodItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    food_item = models.CharField(max_length=200, null=False, blank=False)
    num_of_calories = models.IntegerField(null=True, blank=True)
    calories_exceeded = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    max_calories = models.IntegerField(validators=(MinValueValidator(1, message="Minimum calories for a day should be 1."),))

    def __str__(self):
        return f"User: {self.user}, Max_calories: {self.max_calories}"


class FoodFilter(RQLFilterClass):
    MODEL = FoodItem
    SELECT = True
    FILTERS = [
        'id', {
            'filter':'item',
            'source':'food_item',
            'search':True
        }, {
            'filter':'consumer',
            'source':'user__username',
            'search': True,
        }, {
            'filter':'date',
            'source':'timestamp',
        }, {
        # Some fields may have no DB representation or non-typical ORM filtering
        # `custom` option must be set to True for such fields
        'filter': 'custom_filter',
        'custom': True,
        'lookups': {FilterLookups.EQ, FilterLookups.IN, FilterLookups.I_LIKE},
        'ordering': True,
        'search': True,
        
        'custom_data': [1],
    }]