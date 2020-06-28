from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django_filters import rest_framework as filters

User = get_user_model()
# Create your models here.
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


class FoodFilter(filters.FilterSet):
    class Meta:
        model = FoodItem
        fields = {
            'num_of_calories':['lt', 'gt', 'exact', 'lte', 'gte'],
            'food_item':['exact', 'icontains'],
            'timestamp':['lt', 'gt', 'exact', 'lte', 'gte'],
        }

