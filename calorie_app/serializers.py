from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate
from calorie_app.models import UserProfile, FoodItem
from datetime import datetime
from django.db.models import Sum
import requests, json, pprint

class FoodItemSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = FoodItem
        read_only_fields = ['user', 'timestamp', 'calories_exceeded']
        exclude = ['id',]
        ordering = ['-timestamp']

    # def validate(self, data):
    #     print(self.)
    #     if value.strip() =='':
    #         pass
    #     if value < 1:
    #         raise ValidationError({"num_of_calories":"Please enter a calorie value more than 1."}, code=404)
    #     return value
    def validate(self, data):
        food_item = data['food_item']
        num_of_calories = data['num_of_calories']

        if num_of_calories == 0 or num_of_calories is None  or num_of_calories.strip() == '':       
            HEADERS = {
                "x-app-id":"f26e0228",
                "x-app-key":"130a3ebf8a86195fe3f8632d6b346c1b",
                "Content-Type": "application/json"
            }

            url = f"https://trackapi.nutritionix.com/v2/search/instant?query={food_item}"
            response = requests.get(url, headers=HEADERS)
            json_output = json.loads(response.content.decode('utf-8'))
            # pprint.pprint(data['branded'][0])
            if len(json_output['branded'])>0:
                pprint.pprint(json_output['branded'][0]['nf_calories'])
                data["num_of_calories"] = json_output['branded'][0]['nf_calories']
            else:
                raise ValidationError({"food_item":"Please check the item and try again!"},404)
        return data


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        max_calories = validated_data['user'].profile.max_calories
        calories_consumed_today = FoodItem.objects.filter(
            user=validated_data['user'], 
            timestamp__gte=datetime.now().replace(hour=0, minute=0, second=0)
            ).aggregate(Sum('num_of_calories'))['num_of_calories__sum']
        if calories_consumed_today is not None:
            validated_data['calories_exceeded'] = calories_consumed_today > max_calories

        fooditem = FoodItem.objects.create(**validated_data)        
        return fooditem


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username',"")
        password = data.get('password',"")

        if username and password:
            user = authenticate(**data)
            if user:
                if user.is_active:
                    data['user']=user
                else:
                    raise ValidationError("Your account has been suspended", code=404)
            else:
                raise ValidationError("Please check your credentials and try again!", code=401)
        else:
            raise ValidationError("Please enter both username and password to login!", code=401)
        return data


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = UserProfile
        fields = ['user', 'max_calories']
        extra_kwargs = {'user':{'read_only':True}}

    def valiadate_max_calories(self, value):
        if value < 1:
            raise ValidationError({"max_calories":"Please enter a calorie value more than 1."}, code=404)
        return value        


class UserRegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    groups = serializers.SlugRelatedField(many=True,required=False, queryset=Group.objects.all(),slug_field='name')

    class Meta:
        model = User
        fields = ['username', 'password', 'profile', 'groups']
        extra_kwargs = {'password':{'write_only':True,'style':{'input_type':'password'}}}

    def create(self, validated_data):
        profile_data, password, groups = validated_data.pop('profile'), validated_data.pop('password'), validated_data.pop('groups')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        for group in groups:
            user.groups.add(group)
        UserProfile.objects.create(user=user, max_calories=profile_data['max_calories'])
        user.save()
        return user