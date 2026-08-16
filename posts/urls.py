from django.urls import path, include

from rest_framework import routers

from posts.views import PostViewSet, CommentViewSet


app_name="posts"

router = routers.DefaultRouter()
router.register("posts", PostViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<int:post_pk>/comments/", CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="post-comment-list",
    ),
    path(
        "posts/<int:post_pk>/comments/<int:pk>/", CommentViewSet.as_view(
            {
                "get": "retrieve", "put": "update", "patch": "partial_update",
                "delete": "destroy"
            }
        ), name="post-comment-detail",
    )
]
