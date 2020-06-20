from django.shortcuts import render
from rest_framework.views import APIView
from calorie_app.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    FoodItemSerializer
)
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListCreateAPIView 
from rest_framework.authtoken.models import Token
from calorie_app.models import FoodItem
from rest_framework.permissions import DjangoModelPermissions
from django.contrib.auth.models import User
from .permissions import IsOwnerOrAdmin
from rest_framework import viewsets
# Create your views here.

class FoodItemView(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        return FoodItem.objects.all()

class UserRegisterView(ListCreateAPIView):
    """
    View to create User
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    # def post(self, request):
    #     serializer = UserRegisterSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(data=serializer.data, status=201)


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"token":token.key}, status=201)