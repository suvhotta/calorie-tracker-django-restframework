import json

from django.contrib.auth import get_user_model, models
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

import calorie_app.views as apiviews
from calorie_app.models import FoodItem, UserProfile


class TestingAPI(APITestCase):
    urlpatterns = [
        path('', include('calorie_app.urls')),
    ]
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.view = apiviews.UserRegisterView.as_view({'get':'list'})
        self.url = '/register/'

        #creating different permission-groups
        group_list = ["Administrator", "User_Manager", "Normal_User"]
        for group in group_list:
            TestingAPI.create_group(group)

        #creating an Admin account
        self.user1 = self.setup_user('user1','user1', "Administrator", 2050)
        self.token1 = TestingAPI.token_creation(self.user1)

        #Creating a User_Manager account
        self.user2 = self.setup_user('user2', 'user2', "User_Manager", 1990)
        self.token2 = TestingAPI.token_creation(self.user2)
        
        #Creating a Normal_User account
        self.user3 = self.setup_user('user3', 'user3', 'Normal_User', 2100)
        self.token3 = TestingAPI.token_creation(self.user3)

    @staticmethod
    def token_creation(user):
        token = Token.objects.create(user=user)
        token.save()
        return token

    @staticmethod
    def create_group(group_name):
        model_names = ['fooditem', 'userprofile', 'user']
        new_group, _ = models.Group.objects.get_or_create(name=group_name)
        if group_name == "Administrator":
            for _ in range(len(model_names)):
                new_group = TestingAPI.create_permissions(new_group, model_names[_])
        elif group_name == "User_Manager":
            for _ in range(1, len(model_names)):
                new_group = TestingAPI.create_permissions(new_group, model_names[_])
        elif group_name == "Normal_User":
            new_group = TestingAPI.create_permissions(new_group, model_names[0])

    @staticmethod
    def create_permissions(group, model_name):
        model_names = {
            "fooditem":FoodItem,
            "user":models.User,
            "userprofile":UserProfile
        }
        content_type = ContentType.objects.get_for_model(model_names[model_name])
        add_permission, _ = models.Permission.objects.get_or_create(
            codename=f'can_add_{model_name}',
            name=f'can add {model_name}',
            content_type=content_type
        )
        change_permission, _ = models.Permission.objects.get_or_create(
            codename=f'can_change_{model_name}',
            name=f'can change {model_name}',
            content_type=content_type
        )
        view_permission, _ = models.Permission.objects.get_or_create(
            codename=f'can_view_{model_name}',
            name=f'can view {model_name}',
            content_type=content_type
        )
        delete_permission, _ = models.Permission.objects.get_or_create(
            codename=f'can_delete_{model_name}',
            name=f'can delete {model_name}',
            content_type=content_type
        )
        group.permissions.set([add_permission, delete_permission, change_permission, view_permission])
        return group

    @staticmethod
    def setup_user(username, password, group_name, max_calories):
        User = get_user_model()
        user = User.objects.create(
            username=username,
        )
        user.set_password(password)
        group,_ = models.Group.objects.get_or_create(name=group_name)    
      
        user.groups.add(group)
        user.save()
        UserProfile.objects.create(user=user, max_calories=max_calories)
        return user

    def test_get_all_users_list(self):      
        request = self.factory.get(self.url,
            HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.view(request)
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')

    def test_login_user(self):
        self.valid_payload = {
            "username":"user1",
            "password":"user1"
        }
        response = self.client.post(
            reverse('login'),
            self.valid_payload
        )
        self.assertEqual(response.status_code, 201,
                         'Expected Response Code 201, received {0} instead.'
                         .format(response.status_code))
        self.assertTrue("token" in json.loads(response.content))

    def test_authentication_without_password(self):
        response = self.client.post(self.url, {"username": "snowman"})
        self.assertEqual(400, response.status_code)

    def test_authentication_with_wrong_password(self):
        response = self.client.post(self.url, {"username": self.user1.username, "password": "I_know"})
        self.assertEqual(400, response.status_code)

    def test_admin_get_user_details(self):
        response = self.client.get(
            reverse('user-details', kwargs={'pk':self.user2.pk}),
            HTTP_AUTHORIZATION=f'Token {self.token1.key}'
        )
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')
        self.assertEqual(response.data, {'username':'user2', 'profile':{'user':'user2','max_calories':1990}, 'groups':['User_Manager']})

    def test_admin_add_new_user(self):
        self.valid_payload = {
            "username":"user4",
            "password":"user4",
            "groups":['Normal_User'],
            "profile":{
                "max_calories":1920
            }
        }
        response = self.client.post(
            reverse('register'),
            self.valid_payload, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token1.key}'
        )
        self.assertEqual(response.status_code, 201, f'Expected Response Code 201, received {response.status_code} instead.')

    def test_unique_username_validation(self):
        """
        Test to verify that a post call with already exists username
        """
        user_data_1 = {
            "username":"user4",
            "password":"user4",
            "groups":['Normal_User'],
            "profile":{
                "max_calories":1920
            }
        }
        response = self.client.post(
            reverse('register'),
            user_data_1, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token1.key}'
        )
        self.assertEqual(201, response.status_code)

        user_data_2 = {
            "username":"user4",
            "password":"user4",
            "groups":['Normal_User'],
            "profile":{
                "max_calories":1920
            }
        }
        response = self.client.post(
            reverse('register'),
            user_data_2, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token1.key}'
        )

    def test_admin_remove_user(self): 
        response = self.client.delete(
            reverse('user-details', kwargs={'pk': self.user2.pk}),
            HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        self.assertEqual(response.status_code, 204, f'Expected Response Code 204, received {response.status_code} instead.')

    def test_admin_patch_user(self):
        self.valid_payload={
            "profile":{
                "max_calories":2120
            }
        }
        response = self.client.patch(
            reverse('user-details', kwargs={'pk': self.user2.pk}),
            self.valid_payload, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')

    def test_admin_put_user(self):
        self.valid_payload={
            "username":self.user2.username,
            "password":self.user2.password,
            "profile":{
                "user":"user2",
                "max_calories":2120
            },
            "groups":['User_Manager']
        }
        response = self.client.put(
            reverse('user-details', kwargs={'pk': self.user2.pk}),
            self.valid_payload, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')

    def test_user_manager_add_new_user(self):
        self.valid_payload = {
            "username":"user4",
            "password":"user4",
            "groups":['Normal_User'],
            "profile":{
                "max_calories":1920
            }
        }
        response = self.client.post(
            reverse('register'),
            self.valid_payload, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token2.key}'
        )
        self.assertEqual(response.status_code, 201, f'Expected Response Code 201, received {response.status_code} instead.')

    def test_user_manager_remove_user(self): 
        response = self.client.delete(
            reverse('user-details', kwargs={'pk': self.user3.pk}),
            HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        self.assertEqual(response.status_code, 204, f'Expected Response Code 204, received {response.status_code} instead.')

    def test_user_manager_patch_user(self):
        self.valid_payload={
            "profile":{
                "max_calories":2120
            }
        }
        response = self.client.patch(
            reverse('user-details', kwargs={'pk': self.user3.pk}),
            self.valid_payload, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')

    def test_user_manager_put_user(self):
        self.valid_payload={
            "username":self.user3.username,
            "password":self.user3.password,
            "profile":{
                "user":"user3",
                "max_calories":2120
            },
            "groups":['User_Manager']
        }
        response = self.client.put(
            reverse('user-details', kwargs={'pk': self.user3.pk}),
            self.valid_payload, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')
