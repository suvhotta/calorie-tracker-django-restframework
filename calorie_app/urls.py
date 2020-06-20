from django.urls import path
from calorie_app import views as app_views

urlpatterns = [
    path('register/', app_views.UserRegisterView().as_view()),
    path('login/', app_views.UserLoginView.as_view()),
    path('fooditem/', app_views.FoodItemView.as_view()),
]