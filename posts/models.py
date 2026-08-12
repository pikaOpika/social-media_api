import os
from uuid import uuid4

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

def post_image_file_path(instance, filename):
    _, suffix = os.path.splitext(filename)
    title = slugify(instance.title)
    filename = f"{title}-{uuid4()}{suffix}"
    return os.path.join("posts/post_image/", filename)

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to=post_image_file_path, blank=True)
    liked_by = models.ManyToManyField(get_user_model(), related_name="posts_liked", blank=True)
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)
    publish_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post: {self.title}"



class Comment(models.Model):
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment {self.pk}"

