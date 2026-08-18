from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from datetime import timedelta

from posts.models import Post
from posts.tasks import publish_due_posts

POSTS_URL = reverse("posts:post-list")

def like_url(post_id):
    return reverse("posts:post-like", args=[post_id])

def unlike_url(post_id):
    return reverse("posts:post-unlike", args=[post_id])


class UnauthenticatedPostApiTest(APITestCase):
    def test_annonymus_cant_create_post(self):
        payload = {
            "title": "Test",
            "content": "test test"
        }
        response = self.client.post(POSTS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.count(), 0)


class AuthenticatedPostApiTest(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            email="a@gmail.com",
            username="neb",
            password="a"
        )
        self.user2 = get_user_model().objects.create_user(
            email="b@gmail.com",
            username="shmunya",
            password="b"
        )
        self.user3 = get_user_model().objects.create_user(
            email="c@gmail.com",
            username="yugin",
            password="c"
        )
        self.post = Post.objects.create(
            title="Test",
            content="test",
            author=self.user1
        )

    def test_like_adds_user_to_liked_by(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(like_url(self.post.id))
        self.assertIn(self.user2, self.post.liked_by.all())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_like_twice_does_not_duplicate(self):
        self.client.force_authenticate(user=self.user2)
        self.client.post(like_url(self.post.id))
        self.client.post(like_url(self.post.id))
        self.assertEqual(self.post.liked_by.count(), 1)

    def test_two_users_can_like_same_post(self):
        self.client.force_authenticate(user=self.user2)
        self.client.post(like_url(self.post.id))
        
        self.client.force_authenticate(user=self.user3)
        self.client.post(like_url(self.post.id))

        self.assertIn(self.user2, self.post.liked_by.all())
        self.assertIn(self.user3, self.post.liked_by.all())
        self.assertEqual(self.post.liked_by.count(), 2)

    def test_unlike_removes_user_from_liked_by(self):
        self.client.force_authenticate(user=self.user2)
        self.post.liked_by.add(self.user2)
        response = self.client.post(unlike_url(self.post.id))
        self.assertEqual(self.post.liked_by.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unlike_without_like_does_not_fail(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(unlike_url(self.post.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post.liked_by.count(), 0)

    def test_liked_posts_page(self):
        self.post.liked_by.add(self.user2)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse("posts:post-liked-posts"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.post.id, ids)

    def test_feed_page(self):
        self.client.force_authenticate(user=self.user1)
        self.post2 = Post.objects.create(
            title="Test1",
            content="some text",
            author=self.user2
        )
        self.post3 = Post.objects.create(
            title="Test2",
            content="some text",
            author=self.user3
        )
        self.user1.following.add(self.user2)

        response = self.client.get(reverse("posts:post-feed"))
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.post2.id, ids)
        self.assertIn(self.post.id, ids)
        self.assertNotIn(self.post3.id, ids)

    def test_publish_at(self):
        self.post_publish_at = Post.objects.create(
            title="Hello",
            content="its content",
            publish_at=timezone.now() + timedelta(minutes=5),
            author=self.user2
        )
        self.client.force_authenticate(self.user1)
        response = self.client.get(POSTS_URL)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {self.post.id})
        self.client.force_authenticate(self.user2)
        response = self.client.get(POSTS_URL)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {self.post.id, self.post_publish_at.id})






class PublishDuePostsTaskTest(APITestCase):
    def test_publishes_only_overdue_posts(self):
        author = get_user_model().objects.create_user(
            email="d@gmail.com", username="author", password="test1234"
        )
        overdue = Post.objects.create(
            title="Overdue",
            content="text",
            author=author,
            publish_at=timezone.now() - timedelta(minutes=5),
        )
        future = Post.objects.create(
            title="Future",
            content="text",
            author=author,
            publish_at=timezone.now() + timedelta(days=1),
        )

        publish_due_posts()

        overdue.refresh_from_db()
        future.refresh_from_db()

        self.assertTrue(overdue.is_published)
        self.assertFalse(future.is_published)
