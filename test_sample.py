import json
from datetime import datetime
from django.contrib.auth import get_user_model, models
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

import calorie_app.views as apiviews
from calorie_app.serializers import UserRegisterSerializer, ProfileSerializer
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
        test_cases = [
            {
                "name":"by_admin",
                "user":self.user1,
                "token":self.token1.key,
            }, {
                "name":"by_UserManager",
                "user":self.user2,
                "token":self.token2.key,
            }, {
                "name":"by_NormalUser",
                "user":self.user3,
                "token":self.token3.key,
            }
        ]
        for i in range(len(test_cases)):
            response = self.client.get(
                reverse('users'),
                HTTP_AUTHORIZATION=f'Token {test_cases[i]["token"]}'    
            )
            self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')
            users = get_user_model().objects.all()
            #users with groups Normal_User will only be able to see their details
            if test_cases[i]["user"].groups.filter(name="Normal_User").exists():
                users = get_user_model().objects.filter(username=test_cases[i]["user"].username)
            user_serializer = UserRegisterSerializer(users, many=True)
            self.assertEqual(response.data['results'], user_serializer.data)           

    def test_login_user(self):
        test_cases = [
            {
                "name":"Admin_login",
                "username":self.user1.username,
                "token":self.token1.key,
                "password":'user1',
                "status_code":201,
            }, {
                "name":"User_manager_login",
                "username":self.user2.username,
                "token":self.token2.key,
                "password":'user2',
                "status_code":201,
            }, {
                "name":"Normal_User_login",
                "username":self.user3.username,
                "token":self.token3.key,
                "password":'user3',
                "status_code":201,
            }, {
                "name":"Without_pwd_login",
                "username":self.user1.username,
                "password":"",
                "status_code":400,
            }, {
                "name":"Wrong_pwd_login",
                "username":"user1",
                "password":"user1"+"abc",
                "status_code":400,
            }
        ]

        for i in range(len(test_cases)):
            payload = {
                "username":test_cases[i]["username"],
                "password":test_cases[i]["password"],
            }
            response = self.client.post(
                reverse('login'),
                payload
            )
            self.assertEqual(response.status_code, test_cases[i]["status_code"],
                         f'Expected Response Code {test_cases[i]["status_code"]}, received {response.status_code} instead.')

            if(test_cases[i]["status_code"]) == 201:
                self.assertEqual(response.data["token"], test_cases[i]["token"])
                         
    def test_get_user_details(self):
        test_cases = [
            {
                "name":"Admin get user details",
                "user":self.user1,
                "check_users": [self.user2, self.user3],
                "token":self.token1.key,
                "expected_status_code":200,
            }, {
                "name":"User_Manager get user details",
                "user":self.user2,
                "check_users": [self.user1, self.user3],
                "token":self.token2.key,
                "expected_status_code":200,
            }, {
                "name":"Normal_User get user details",
                "user":self.user3,
                "check_users": [self.user1, self.user2],
                "token":self.token3.key,
                "expected_status_code":404,
            }
        ]
        
        for i in range(len(test_cases)):
            for user in test_cases[i]["check_users"]:
                response = self.client.get(
                    reverse('user-details', kwargs={'pk':user.pk}),
                    HTTP_AUTHORIZATION=f'Token {test_cases[i]["token"]}'
                )
                self.assertEqual(response.status_code, test_cases[i]["expected_status_code"], f'Expected Response Code {test_cases[i]["expected_status_code"]}, received {response.status_code} instead.')
                if test_cases[i]["expected_status_code"] == 200:                    
                    self.assertEqual(response.data['username'], user.username)
                    self.assertEqual(response.data['id'], user.pk)

    def test_add_new_user(self):
        test_cases = [
            {
                "name":"By_Admin",
                "user_data": {
                    "username":"user4",
                    "password":"user4",
                    "groups":["Normal_User"],
                    "profile":{
                        "max_calories":1920
                    }
                },
                "token":self.token1.key,
                "expected_code":201,
            }, {
                "name":"By_User_Manager",
                "user_data": {
                    "username":"user5",
                    "password":"user5",
                    "groups":["Normal_User"],
                    "profile":{
                        "max_calories":2120
                    }
                },
                "token":self.token2.key,
                "expected_code":201,
            }, {
                "name":"By_Normal_User",
                "user_data": {
                    "username":"user6",
                    "password":"user6",
                    "groups":["Normal_User"],
                    "profile":{
                        "max_calories":2120
                    }
                },
                "token":self.token3.key,
                "expected_code":403,
            }, {
                "name":"non_existing_group",
                "user_data": {
                    "username":"user6",
                    "password":"user6",
                    "groups":["gibberish"],
                    "profile":{
                        "max_calories":2120
                    }
                },
                "token":self.token2.key,
                "expected_code":400,
            }, {
                "name":"missing_username",
                "user_data": {
                    "username":"",
                    "password":"user6",
                    "groups":["Normal_User"],
                    "profile":{
                        "max_calories":2120
                    }
                },
                "token":self.token2.key,
                "expected_code":400,
            }, {
                "name":"missing_password",
                "user_data": {
                    "username":"user6",
                    "password":"",
                    "groups":["Normal_User"],
                    "profile":{
                        "max_calories":2120
                    }
                },
                "token":self.token2.key,
                "expected_code":400,
            }, {
                "name":"missing_groups",
                "user_data": {
                    "username":"user6",
                    "password":"acv",
                    "groups":[],
                    "profile":{
                        "max_calories":2120
                    }
                },
                "token":self.token2.key,
                "expected_code":400,
            }, {
                "name":"missing_max_calories",
                "user_data": {
                    "username":"user6",
                    "password":"",
                    "groups":["Normal_User"],
                },
                "token":self.token2.key,
                "expected_code":400,
            }, {
                "name":"max_calories_zero",
                "user_data": {
                    "username":"user6",
                    "password":"acv",
                    "groups":["Normal_User"],
                    "profile":{
                        "max_calories":0
                    }
                },
                "token":self.token2.key,
                "expected_code":400,
            }, {
                "name":"existing_username",
                "user_data": {
                    "username":"user3",
                    "password":"acv",
                    "groups":["Normal_User"],
                    "profile":{
                        "max_calories":1270
                    }
                },
                "token":self.token2.key,
                "expected_code":400,
            }
            
        ]
        for i in range(len(test_cases)):
            response = self.client.post(
                reverse('register'),
                test_cases[i]["user_data"], format="json",
                HTTP_AUTHORIZATION=f'Token {test_cases[i]["token"]}'
            )
            self.assertEqual(response.status_code, test_cases[i]["expected_code"], f'Expected Response Code {test_cases[i]["expected_code"]}, received {response.status_code} instead.')
            if response.status_code == 201:
                user = get_user_model().objects.filter(username=test_cases[i]["user_data"]["username"]).first()
                response = self.client.get(
                    reverse('user-details', kwargs={'pk':user.pk}),
                    HTTP_AUTHORIZATION=f'Token {test_cases[i]["token"]}'
                )
                self.assertEqual(response.data['username'], user.username)
                self.assertEqual(response.data['id'], user.pk)
                self.assertEqual(response.data['groups'], [g.name for g in user.groups.all()])
                self.assertEqual(response.data['profile']['max_calories'], user.profile.max_calories)
                self.assertEqual(response.data['profile']['user'], user.profile.user.username)

    def test_remove_user(self):
        test_cases = [
            {
                "name":"by_Normal_User",
                "removed_user":self.user1,
                "token":self.token3.key,
                "expected_code":404,
            }, {
                "name":"by_admin",
                "removed_user":self.user3,
                "token":self.token1.key,
                "expected_code":204,
            }, {
                "name":"by_User_Manager",
                "removed_user":self.user1,
                "token":self.token2.key,
                "expected_code":204,
            }, {
                "name":"deleting_self",
                "removed_user":self.user2,
                "token":self.token2.key,
                "expected_code":204,
            }
        ]

        for i in range(len(test_cases)):
            response = self.client.delete(
                reverse('user-details', kwargs={'pk':test_cases[i]["removed_user"].pk}),
                HTTP_AUTHORIZATION=f'Token {test_cases[i]["token"]}'
            )
            self.assertEqual(response.status_code, test_cases[i]["expected_code"], f'Expected Response Code {test_cases[i]["expected_code"]}, received {response.status_code} instead.')
            if response.status_code == 204:
                user = get_user_model().objects.filter(id=test_cases[i]['removed_user'].pk).exists()
                self.assertEqual(user, False)
                
    def test_edit_user_details(self):
        test_cases = [
            {
                "name":"by_admin",
                "payload":{
                    "profile":{
                        "max_calories":2123
                    }
                },
                "user":self.user2,
                "token":self.token1.key,
                "method":self.client.patch,
                "expected_code":200,
            }, {
                "name":"by_User_Manager",
                "payload":{
                    "username":"user4"
                },
                "user":self.user1,
                "token":self.token2.key,
                "method":self.client.patch,
                "expected_code":200,
            }, {
                "name":"by_Normal_User",
                "payload":{
                    "groups":["User_Manager",]
                },
                "user":self.user2,
                "token":self.token3.key,
                "method":self.client.patch,
                "expected_code":404,
            }, {
                "name":"patch_Groups",
                "payload":{
                    "groups":["Administrator",]
                },
                "user":self.user2,
                "token":self.token1.key,
                "method":self.client.patch,
                "expected_code":200,
            }, {
                "name":"put_user_details",
                "payload":{
                    "username":self.user2.username,
                    "password":self.user2.username,
                    "profile":{
                        "user":"user2",
                        "max_calories":2120
                    },
                "groups":['User_Manager']
                },
                "user":self.user2,
                "token":self.token1.key,
                "method":self.client.put,
                "expected_code":200,
            }
        ]

        for i in range(len(test_cases)):
            response = test_cases[i]["method"](
                reverse('user-details', kwargs={'pk': test_cases[i]["user"].pk}),
                test_cases[i]["payload"], format="json",
                HTTP_AUTHORIZATION=f'Token {test_cases[i]["token"]}')
            self.assertEqual(response.status_code, test_cases[i]["expected_code"], f'Expected Response Code {test_cases[i]["expected_code"]}, received {response.status_code} instead.')

            if(response.status_code == 200):
                for key, value in test_cases[i]["payload"].items():
                    #checking if it is a nested dictionary, for profile.max_calories
                    if isinstance(value, dict):
                        for key1 in value.keys():
                            self.assertEqual(dict(response.data.get(key)).get(key1), test_cases[i]["payload"][key][key1])        
                    #not checking the password field as it is write-only and won't be returned in the response.
                    elif key == "password":
                        pass
                    else:
                        self.assertEqual(response.data.get(key), test_cases[i]["payload"][key])
       
    def test_add_fooditem(self):
        test_cases = [
            {
                "name":"with calories",
                "payload":{
                    "food_item":"Friedrice",
                    "num_of_calories":450
                },
                "token":self.token1.key,
                "method":self.client.post,
                "expected_code":201
            }, {
                "name":"without_calories",
                "payload":{
                    "food_item":"Chicken burger",
                },
                "token":self.token2.key,
                "method":self.client.post,
                "expected_code":201
            }, {
                "name":"gibberish_food_item_in_api",
                "payload":{
                    "food_item":"asdasdasd"
                },
                "token":self.token2.key,
                "method":self.client.post,
                "expected_code":400
            }
        ]

        for i in range(len(test_cases)):
            response = test_cases[i]["method"](
                reverse('fooditem'),
                test_cases[i]["payload"],
                HTTP_AUTHORIZATION = f'token {test_cases[i]["token"]}'
            )
            self.assertEqual(response.status_code, test_cases[i]["expected_code"], f'Expected Response Code {test_cases[i]["expected_code"]}, received {response.status_code} instead.')
            if response.status_code == 201:
                food_item = FoodItem.objects.filter(id=response.data['id']).first()
                self.assertEqual(test_cases[i]["payload"]["food_item"], food_item.food_item)
                if test_cases[i]["payload"].get("num_of_calories"):
                    self.assertEqual(test_cases[i]["payload"]["num_of_calories"], food_item.num_of_calories)

    def test_view_fooditem(self):
        self.payload = {
            "food_item":"Fried rice",
            "num_of_calories":450
        }
        response1 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token1.key}'
        )
        self.payload = {
            "food_item":"Chicken Soup",
            "num_of_calories":150
        }
        response2 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token2.key}'
        )
        self.payload = {
            "food_item":"Chicken Biryani",
            "num_of_calories":500
        }
        response3 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token3.key}'
        )
        test_cases = [
            {
                "name":"all_food_items_by_admin",
                "view":"fooditem",
                "token":self.token1.key,
                "method":self.client.get,
                "expected_code":200,
            }, {
                "name":"all_food_items_by_user_manager",
                "view":"fooditem",
                "token":self.token2.key,
                "method":self.client.get,
                "expected_code":200,
            }, {
                "name":"all_food_items_by_Normal_User",
                "view":"fooditem",
                "token":self.token2.key,
                "method":self.client.get,
                "expected_code":200,
            }, {
                "name":"self_check",
                "token":self.token3.key,
                "view":"food-details",
                "method":self.client.get,
                "expected_code":200,
                "food_id":response3.data['id'],
            }, {
                "name":"admin_check_others",
                "token":self.token1.key,
                "view":"food-details",
                "method":self.client.get,
                "expected_code":200,
                "food_id":response2.data['id'],
            }, {
                "name":"User_manager_check_others",
                "token":self.token2.key,
                "view":"food-details",
                "method":self.client.get,
                "expected_code":404,
                "food_id":response3.data['id'],
            }, {
                "name":"Normal_User_check_others",
                "token":self.token3.key,
                "view":"food-details",
                "method":self.client.get,
                "expected_code":404,
                "food_id":response1.data['id'],
            }, 
        ]

        for i in range(len(test_cases)):
            if test_cases[i]["view"] == "fooditem":
                response = test_cases[i]["method"](
                    reverse('fooditem'),
                    HTTP_AUTHORIZATION = f'token {test_cases[i]["token"]}'
                )
                self.assertEqual(response.status_code, test_cases[i]["expected_code"], f'Expected Response Code {test_cases[i]["expected_code"]}, received {response.status_code} instead.')
                if "admin" in test_cases[i]["name"]:
                    self.assertEqual(response.data['count'], 3)
                else:
                    self.assertEqual(response.data['count'], 1)
            else:
                response = test_cases[i]["method"](
                    reverse('food-details', kwargs={'pk':test_cases[i]["food_id"]}),
                    HTTP_AUTHORIZATION = f'token {test_cases[i]["token"]}'
                )      
                self.assertEqual(response.status_code, test_cases[i]["expected_code"], f'Expected Response Code {test_cases[i]["expected_code"]}, received {response.status_code} instead.')

    def test_edit_delete_fooditems(self):
        self.payload = {
            "food_item":"Fried rice",
            "num_of_calories":450
        }
        response1 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token1.key}'
        )
        self.payload = {
            "food_item":"Chicken Soup",
            "num_of_calories":150
        }
        response2 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token2.key}'
        )
        self.payload = {
            "food_item":"Chicken Biryani",
            "num_of_calories":500
        }
        response3 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token3.key}'
        )
        test_cases = [
            {
                "name":"edit_by_admin",
                "token":self.token1.key,
                "method":self.client.get,
                "food_id":response2.data['id'],
                "expected_code":200,
            }, {
                "name":"edit_by_UserManager",
                "token":self.token2.key,
                "method":self.client.get,
                "food_id":response1.data['id'],
                "expected_code":404,
            }, {
                "name":"edit_by_NormalUser",
                "token":self.token2.key,
                "method":self.client.get,
                "food_id":response1.data['id'],
                "expected_code":404,
            }, {
                "name":"fooditem_patch_method",
                "payload":{
                    "num_of_calories":450
                },
                "token":self.token1.key,
                "method":self.client.patch,
                "food_id":response3.data['id'],
                "expected_code":200
            }, {
                "name":"fooditem_delete_method",
                "token":self.token1.key,
                "method":self.client.delete,
                "food_id":response3.data['id'],
                "expected_code":204
            }
        ]

        for i in range(len(test_cases)):
            if "patch" in test_cases[i]["name"]:
                response = test_cases[i]["method"](
                    reverse('food-details', kwargs={'pk':test_cases[i]["food_id"]}),
                    test_cases[i]["payload"], 
                    HTTP_AUTHORIZATION = f'token {test_cases[i]["token"]}'
                )

                self.assertEqual(response.status_code, test_cases[i]["expected_code"], f'Expected Response Code {test_cases[i]["expected_code"]}, received {response.status_code} instead.')
                if response.status_code == 200:
                    for key in test_cases[i]["payload"].keys():
                        payload_data = test_cases[i]["payload"][key]
                        food_data = FoodItem.objects.filter(id=test_cases[i]["food_id"]).all().values(key).first()[key]
                        self.assertEqual(food_data, payload_data)

            elif "delete" in test_cases[i]["name"]:
                response = response = test_cases[i]["method"](
                    reverse('food-details', kwargs={'pk':test_cases[i]["food_id"]}),
                    HTTP_AUTHORIZATION = f'token {test_cases[i]["token"]}'
                )

                self.assertEqual(response.status_code, test_cases[i]["expected_code"], f'Expected Response Code {test_cases[i]["expected_code"]}, received {response.status_code} instead.')
                if response.status_code == 204:
                    food_data = FoodItem.objects.filter(id=test_cases[i]["food_id"]).exists()
                    self.assertEqual(False,food_data)

    def test_filters(self):
        self.payload = {
            "food_item":"Fried rice",
            "num_of_calories":450
        }
        response1 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token1.key}'
        )
        self.payload = {
            "food_item":"Chicken Soup",
            "num_of_calories":150
        }
        response2 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token2.key}'
        )
        self.payload = {
            "food_item":"Chicken Biryani",
            "num_of_calories":500
        }
        response = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token3.key}'
        )
        self.payload = {
            "food_item":"Chicken Pizza",
            "num_of_calories":600
        }
        response4 = self.client.post(
            reverse('fooditem'),
            self.payload,
            HTTP_AUTHORIZATION = f'token {self.token3.key}'
        )

        url = f"{reverse('fooditem')}?(id=eq=1|like(item,*Pizza*))"
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION = f'token {self.token1.key}'
        )
        items = FoodItem.objects.filter(id=1)|FoodItem.objects.filter(food_item__icontains='Pizza')
        self.assertEqual(response.data['count'], items.count())


        url = f"{reverse('fooditem')}?(date=lt={datetime.now()}&like(item,*Rice*))"
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION = f'token {self.token1.key}'
        )
        items = FoodItem.objects.filter(timestamp__lt=datetime.now()).filter(food_item__icontains='Rice')
        self.assertEqual(response.data['count'], items.count())

        url = f"{reverse('fooditem')}?(consumer=eq=user2&like(item,*Rice*))"
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION = f'token {self.token1.key}'
        )
        items = FoodItem.objects.filter(user__username='user2').filter(food_item__icontains='Rice')
        self.assertEqual(response.data['count'], items.count())
