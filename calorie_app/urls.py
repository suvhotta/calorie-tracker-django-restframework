from django.urls import path
from calorie_app import views as app_views

fooditem_list = app_views.FoodItemView.as_view({
    'get':'list',
    'post':'create'
}
)

fooditem_detail = app_views.FoodItemView.as_view(
    {
        'get':'retrieve',
        'put':'update',
        'patch':'partial_update',
        'delete':'destroy'
    }
)
register = app_views.UserRegisterView.as_view({
    'get':'list',
    'post':'create'
})

users = app_views.UserRegisterView.as_view({
    'get':'retrieve',
    'put':'update',
    'patch':'partial_update',
    'delete':'destroy'
})

urlpatterns = [
    path('register/', register),
    path('users/<int:pk>', users),
    path('login/', app_views.UserLoginView.as_view()),
    path('fooditem/', fooditem_list),
    path('fooditem/<int:pk>/', fooditem_detail),
]