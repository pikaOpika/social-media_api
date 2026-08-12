from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.serializers import UserSerializer

class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]
