from django.contrib.auth import get_user_model
from django.db.models import Count

from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateAPIView
)
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from users.serializers import UserSerializer, UserListSerializer, UserDetailSerializer, UserProfileSerializer

from social_media_settings.schema import DETAIL_RESPONSE

@extend_schema(tags=["register"])
class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]

@extend_schema(tags=["users"])
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]

    def get_queryset(self):
        queryset = self.queryset.annotate(
            count_posts=Count("posts", distinct=True),
            count_followers=Count("followers", distinct=True),
            count_following=Count("following", distinct=True),
        )
        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "followers", "following"]:
            return UserListSerializer
        if self.action == "retrieve":
            return UserDetailSerializer
        return UserSerializer

    @extend_schema(request=None, responses=DETAIL_RESPONSE)
    @action(detail=True, methods=["POST"])
    def follow(self, request, pk=None):
        current_user = self.request.user
        user = self.get_object()
        if current_user == user:
            return Response({"detail": "You cannot follow yourself"},status=status.HTTP_400_BAD_REQUEST)
        current_user.following.add(
            user
        )
        return Response({"detail": "You successfully follow user"}, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=DETAIL_RESPONSE)
    @action(detail=True, methods=["POST"])
    def unfollow(self, request, pk=None):
        current_user = self.request.user
        user = self.get_object()
        current_user.following.remove(user)
        return Response({"detail": "You successfully unfollow"}, status=status.HTTP_200_OK)

    @extend_schema(responses=UserListSerializer(many=True))
    @action(detail=True, methods=["GET"])
    def following(self, request, pk):
        user = self.get_object()
        data = self.get_queryset().filter(followers=user)
        page = self.paginate_queryset(data)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(responses=UserListSerializer(many=True))
    @action(detail=True, methods=["GET"])
    def followers(self, request, pk):
        user = self.get_object()
        data = self.get_queryset().filter(following=user)
        page = self.paginate_queryset(data)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

@extend_schema(tags=["profile"])
class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
