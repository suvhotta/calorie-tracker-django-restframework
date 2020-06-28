from django.contrib.auth import get_user_model, models
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase, APIClient

import calorie_app.views as apiviews
from calorie_app.models import UserProfile


class TestUsers(APITestCase):
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
    def setup_user():
        User = get_user_model()
        user = User.objects.create(
            username="admin1",
            password="admin1",
        )
        groups = models.Group.objects.all()
        print(groups)
        # groups = ['Administrator']
        # for group in groups:
        user.groups.add(models.Group.objects.all()[2])
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
