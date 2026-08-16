from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import filters

from posts.models import Post, Comment
from posts.serializers import (
    PostSerializer, PostListSerializer,
    PostCreateUpdateSerializer, PostDetailSerializer,
    CommentSerializer, CommentListSerializer
)
from posts.permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsAuthorOrReadOnly,]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "hashtags__name"]

    def get_queryset(self):
        queryset = self.queryset.annotate(
            likes=Count("liked_by", distinct=True),
            count_comments=Count("comments", distinct=True)
        )
        return queryset.select_related("author").prefetch_related("hashtags")

    def get_serializer_class(self):
        if self.action in ["create", "partial_update", "update"]:
            return PostCreateUpdateSerializer
        if self.action in ["list", "feed", "liked_posts"]:
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    @action(detail=False, methods=["GET"])
    def feed(self, request):
        data = self.get_queryset().filter(
            Q(author__in=request.user.following.all()) | Q(author=request.user)
        )
        page = self.paginate_queryset(data)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def like(self, request, pk):
        post = self.get_object()
        post.liked_by.add(request.user)
        return Response(
            {"detail": "You liked post"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk):
        post = self.get_object()
        post.liked_by.remove(request.user)
        return Response(
            {"detail": "You unliked post"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["GET"])
    def liked_posts(self, request):
        page = self.paginate_queryset(self.get_queryset().filter(liked_by=request.user))
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post=self.kwargs["post_pk"]).select_related("author")

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=get_object_or_404(Post, pk=self.kwargs["post_pk"]))
