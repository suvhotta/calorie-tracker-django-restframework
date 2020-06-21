from django.shortcuts import render
from calorie_app.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    FoodItemSerializer
)
from rest_framework import generics, viewsets, views
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from calorie_app.models import FoodItem
from django.contrib.auth.models import User
from .permissions import IsOwnerOrAdmin, IsUserManagerOrAdmin
from django_filters import rest_framework as filters


class FoodFilter(filters.FilterSet):
    class Meta:
        model = FoodItem
        fields = {
            'num_of_calories':['lt','gt','exact','lte','gte'],
            'food_item':['exact',],
            'timestamp':['lt','gt','exact','lte','gte'],
        }


class FoodItemView(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = FoodItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FoodFilter
    def get_queryset(self):
        return FoodItem.objects.all()


class UserRegisterView(generics.ListCreateAPIView):
    """
    View to create User
    """
    permission_classes = (IsUserManagerOrAdmin,)
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserRegisterSerializer


class UserLoginView(views.APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"token":token.key}, status=201)