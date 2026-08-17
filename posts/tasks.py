from celery import shared_task
from django.utils import timezone

from posts.models import Post


@shared_task
def publish_due_posts():
    posts = Post.objects.filter(
        publish_at__isnull=False,
        publish_at__lte=timezone.now(),
        is_published=False
    )
    return posts.update(is_published=True)
    