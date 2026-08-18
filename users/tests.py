from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


USERS_URL = reverse("users:user-list")

def follow_url(user_id):
    return reverse("users:user-follow", args=[user_id])

def unfollow_url(user_id):
    return reverse("users:user-unfollow", args=[user_id])

class UnauthenticatedUserApiTest(APITestCase):
    def test_unauthenticated_has_permission_register(self):
        payload = {
            "email": "a@gmail.com",
            "username": "neb",
            "password": "Yhnujm123"
        }
        response = self.client.post(reverse("users:register"), data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthenticatedUserApiTest(APITestCase):
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

    def test_follow_add_to_following(self):
        self.client.force_authenticate(user=self.user1)
        self.client.post(follow_url(self.user2.id))
        self.assertEqual(self.user1.following.count(), 1)
        self.assertIn(self.user2, self.user1.following.all())
        self.assertIn(self.user1, self.user2.followers.all())

    def test_cant_follow_yourself(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(follow_url(self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_follow_two_times(self):
        self.client.force_authenticate(user=self.user1)
        self.client.post(follow_url(self.user2.id))
        self.client.post(follow_url(self.user2.id))
        self.assertEqual(self.user1.following.count(), 1)

    def test_unfollow_removes_from_following(self):
        self.user1.following.add(self.user2)
        self.client.force_authenticate(user=self.user1)
        self.client.post(unfollow_url(self.user2.id))
        self.assertEqual(self.user1.following.count(), 0)
