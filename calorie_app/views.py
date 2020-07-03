from django.contrib.auth.models import User
from django.shortcuts import render
from django_filters import rest_framework as filters
from rest_framework import generics, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from calorie_app.models import FoodFilter, FoodItem
from calorie_app.serializers import (FoodItemSerializer, 
                                    UserLoginSerializer,
                                    UserRegisterSerializer)

from .permissions import IsOwnerOrAdmin, IsUserManagerOrAdmin


class FoodItemView(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = FoodItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FoodFilter
    def get_queryset(self):
        if self.request.user.groups.first().name != "Administrator":
            return FoodItem.objects.filter(user=self.request.user)
        return FoodItem.objects.all()


class UserRegisterView(viewsets.ModelViewSet):
    """
    View to create User
    """
    permission_classes = [IsUserManagerOrAdmin]
    # permissions = [IsUserManagerOrAdmin]
    serializer_class = UserRegisterSerializer

    def get_queryset(self):
        if self.request.user.groups.first().name not in ("Administrator", "User_Manager"):
            return User.objects.filter(username=self.request.user.username).filter(is_staff=False)
                
        return User.objects.filter(is_staff=False).all()
    

class UserLoginView(views.APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token":token.key}, status=201)