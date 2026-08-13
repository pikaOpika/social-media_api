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

from users.serializers import UserSerializer, UserListSerializer, UserDetailSerializer, UserProfileSerializer

from users.pagination import CustomPagination

class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]


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
        if self.action == "list":
            return UserListSerializer
        if self.action == "retrieve":
            return UserDetailSerializer
        return UserSerializer

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

    @action(detail=True, methods=["POST"])
    def unfollow(self, request, pk=None):
        current_user = self.request.user
        user = self.get_object()
        current_user.following.remove(user)
        return Response({"detail": "You successfully unfollow"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def following(self, request, pk):
        user = self.get_object()
        data = user.following.all()
        page = self.paginate_queryset(data)
        serializer = UserListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["GET"])
    def followers(self, request, pk):
        user = self.get_object()
        data = user.followers.all()
        page = self.paginate_queryset(data)
        serializer = UserListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
