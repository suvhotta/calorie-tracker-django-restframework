from django.contrib.auth import get_user_model, models
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase, APIClient
from django.contrib.contenttypes.models import ContentType
import calorie_app.views as apiviews
from calorie_app.models import UserProfile
from calorie_app.models import FoodItem, UserProfile

class TestUserCreation(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.view = apiviews.UserRegisterView.as_view({'get':'list'})
        self.url = '/register/'
        # self.view = apiviews.FoodItemView.as_view({'get':'list'})
        # self.url = '/fooditem/'
        self.user = self.setup_user()
        self.token = Token.objects.create(user=self.user)
        self.token.save()

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
    def setup_user():
        User = get_user_model()
        user = User.objects.create(
            username="admin1",
            password="admin1",
        )
        new_group, created = models.Group.objects.get_or_create(name='Administrator')
        content_type = ContentType.objects.get_for_model(FoodItem)
        new_group = TestUserCreation.create_permissions(new_group, "fooditem", content_type)
        content_type = ContentType.objects.get_for_model(UserProfile)
        new_group = TestUserCreation.create_permissions(new_group, "userprofile", content_type)
        content_type = ContentType.objects.get_for_model(models.User)
        new_group = TestUserCreation.create_permissions(new_group, "user", content_type)
        
        user.groups.add(new_group)
        user.save()
        UserProfile.objects.create(user=user, max_calories=2150)
        return user



    def test_list(self):
        # self.client.login(username='admin1', password='admin1')
        # params = {
        #     'food_item':'chicken lasagna'
        # }
        # response = self.client.post(self.url, params)
        # self.assertEqual(response.status_code, 201,
        #                  'Expected Response Code 201, received {0} instead.'
        #                  .format(response.status_code))
        request = self.factory.get(self.url,
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.view(request)
        self.assertEqual(response.status_code, 200, f'Expected Response Code 200, received {response.status_code} instead.')