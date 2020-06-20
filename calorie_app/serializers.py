from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate
from calorie_app.models import UserProfile, FoodItem
from datetime import datetime
from django.db.models import Sum

group_choices = ['Normal_User', 'User_Manager', 'Administrator']

class FoodItemSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = FoodItem
        read_only_fields = ['user', 'timestamp', 'calories_exceeded']
        exclude = ['id',]
        ordering = ['-timestamp']

    def validate_num_of_calories(self, value):
        if value < 1:
            raise ValidationError({"num_of_calories":"Please enter a calorie value more than 1."}, code=404)
        return value

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
        # food_item = FoodItem.objects.create(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    #Throwing user already exists error when using the class meta
    # class Meta:
    #     model = User
    #     fields = ['username', 'password']
    #     extra_kwargs = {'password':{'write_only':True,'style':{'input_type':'password'}}}

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
    class Meta:
        model = UserProfile
        fields = ['user', 'max_calories']
        extra_kwargs = {'user':{'read_only':True}}

    def valiadate_max_calories(self, value):
        if value < 1:
            raise ValidationError({"max_calories":"Please enter a calorie value more than 1."}, code=404)
        return value        


class GroupSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Group
        fields = ('name',)



class UserRegisterSerializer(serializers.ModelSerializer):
    # groups = serializers.ChoiceField(choices=group_choices)
    profile = ProfileSerializer()
    # groups = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field="name")
    # max_calories = serializers.IntegerField(write_only=True)
    # profile = serializers.RelatedField(many=False, read_only=True)
    # profile = serializers.ReadOnlyField(source='user.profile')
    
    class Meta:
        model = User
        fields = ['username', 'password', 'profile', 'groups']
        extra_kwargs = {'password':{'write_only':True,'style':{'input_type':'password'}}}


    # def valiadate_max_calories(self, value):
    #     if value < 1:
    #         raise ValidationError({"max_calories":"Please enter a calorie value more than 1."}, code=404)
    #     return value    

    # def validate_groups(self, value):
    #     if len(value) > 1:
    #         raise ValidationError({"groups":"You can select only one group"})
    #     return value
        
    def create(self, validated_data):
        profile_data, password, groups = validated_data.pop('profile'), validated_data.pop('password'), validated_data.pop('groups')
        # group = Group.objects.get(name=group_name)
        user = User.objects.create(**validated_data)
        user.set_password(password)
        for group in groups:
            user.groups.add(group)
        UserProfile.objects.create(user=user, max_calories=profile_data['max_calories'])
        user.save()
        print(user.username, user.profile)
        # user.groups, user.max_calories = group_name, profile_max_calories
        return user



