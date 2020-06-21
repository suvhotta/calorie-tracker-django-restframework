from django.shortcuts import render
from calorie_app.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    FoodItemSerializer
)
from rest_framework import generics, viewsets, views
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from calorie_app.models import FoodItem, FoodFilter
from django.contrib.auth.models import User
from .permissions import IsOwnerOrAdmin, IsUserManagerOrAdmin
from django_filters import rest_framework as filters


class FoodItemView(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = FoodItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FoodFilter
    def get_queryset(self):
        if self.request.user.groups.first().name != "Administrator":
            return FoodItem.objects.filter(user=self.request.user)
        return FoodItem.objects.all()

class UserRegisterView(generics.ListCreateAPIView):
    """
    View to create User
    """
    permission_classes = (IsUserManagerOrAdmin,)
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserRegisterSerializer

    def get_queryset(self):
        try:
            if self.request.user.groups.first().name not in ("Administrator", "User_Manager"):
                return User.objects.filter(username=self.request.user.username)
            return User.objects.all()
        except (AttributeError, TypeError):
            print("User isn't authorized here.")
            raise PermissionError("User isn't authorized here.")


class UserLoginView(views.APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token":token.key}, status=201)