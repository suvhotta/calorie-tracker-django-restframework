from django.contrib.auth import get_user_model, models
from django.contrib.contenttypes.models import ContentType
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory, APITestCase
from rest_framework import status
import calorie_app.views as apiviews
from calorie_app.models import FoodItem, UserProfile
from django.test import TestCase
from django.urls import include, path, reverse

class TestUserList(APITestCase):
    urlpatterns = [
        path('', include('calorie_app.urls')),
    ]
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.view = apiviews.UserRegisterView.as_view({'get':'list'})
        self.url = '/register/'
        self.user1 = self.setup_user('user1','user1',"Administrator",2050)
        print(self.user1.pk)
        self.token = TestUserList.token_creation(self.user1)
        
    @staticmethod
    def token_creation(user):
        token = Token.objects.create(user=user)
        token.save()
        return token

    @staticmethod
    def create_permissions(group, model_name, content_type):
        add_permission = models.Permission.objects.create(
            codename=f'can_add_{model_name}',
            name=f'can add {model_name}',
            content_type=content_type
        )
        change_permission = models.Permission.objects.create(
            codename=f'can_change_{model_name}',
            name=f'can change {model_name}',
            content_type=content_type
        )
        view_permission = models.Permission.objects.create(
            codename=f'can_view_{model_name}',
            name=f'can view {model_name}',
            content_type=content_type
        )
        delete_permission = models.Permission.objects.create(
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
    
        new_group, _ = models.Group.objects.get_or_create(name=group_name)
        content_type = ContentType.objects.get_for_model(FoodItem)
        new_group = TestUserList.create_permissions(new_group, "fooditem", content_type)
        content_type = ContentType.objects.get_for_model(UserProfile)
        new_group = TestUserList.create_permissions(new_group, "userprofile", content_type)
        content_type = ContentType.objects.get_for_model(models.User)
        new_group = TestUserList.create_permissions(new_group, "user", content_type)
        
        user.groups.add(new_group)
        user.save()
        UserProfile.objects.create(user=user, max_calories=max_calories)
        return user

    def test_get_all_users_list(self):
        request = self.factory.get(self.url,
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.view(request)
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')

    def test_login_user(self):
        self.valid_payload = {
            "username":"user1",
            "password":"user1"
        }
        
        self.url = reverse('login')

        response = self.client.post(self.url, self.valid_payload)
        print(response.content)
        self.assertEqual(response.status_code, 201,
                         'Expected Response Code 201, received {0} instead.'
                         .format(response.status_code))

    def test_get_user_details(self):
        self.view = apiviews.UserRegisterView.as_view({'get':'retrieve'})
        
        self.user = get_user_model().objects.filter(username='user1').first()
        print(self.user.pk)
        self.token,_ = Token.objects.get_or_create(user=self.user)
        self.url = reverse('user-details',kwargs={'pk':self.user.pk})
        request = self.factory.get(self.url,
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.view(request,pk=self.user.pk)
        
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')
        self.assertEqual(response.data, {'username':'user1', 'profile':{'user':'user1','max_calories':2050}, 'groups':['Administrator']})

    def test_add_new_user(self):
        self.view = apiviews.UserRegisterView.as_view({'post':'create'})
        
        self.user = get_user_model().objects.filter(username='user1').first()
        self.token,_ = Token.objects.get_or_create(user=self.user)
        self.valid_payload = {
            "username":"user2",
            "password":"user2",
            "groups":['Administrator'],
            "profile":{
                "max_calories":1920
            }
        }
        self.url = reverse('register')
        request = self.factory.post(self.url, self.valid_payload, format="json",
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.view(request)
        print(response.data)
        self.assertEqual(response.status_code, 201, f'Expected Response Code 201, received {response.status_code} instead.')
        # self.assertEqual(response.data, {'username':'user1', 'profile':{'user':'user1','max_calories':2050}, 'groups':['Administrator']})
        
