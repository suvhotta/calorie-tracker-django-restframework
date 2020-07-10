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
    'post':'create'
})

userslist = app_views.UserRegisterView.as_view({
    'get':'list',
})

users = app_views.UserRegisterView.as_view({
    'get':'retrieve',
    'put':'update',
    'patch':'partial_update',
    'delete':'destroy'
})

urlpatterns = [
    path('register/', register, name='register'),
    path('users/', userslist, name='users'),
    path('users/<int:pk>/', users, name='user-details'),
    path('login/', app_views.UserLoginView.as_view(), name='login'),
    path('fooditem/', fooditem_list, name='fooditem'),
    path('fooditem/<int:pk>/', fooditem_detail, name='food-details'),
]
