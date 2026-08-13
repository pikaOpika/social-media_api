from rest_framework import serializers

from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username", "password"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {
                    "input_type": "password"
                },
                "min_length": 8
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user



class UserListSerializer(UserSerializer):
    count_posts = serializers.IntegerField(read_only=True)
    count_followers = serializers.IntegerField(read_only=True)
    count_following = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ["id", "username", "image", "count_posts", "count_followers", "count_following"]


class UserDetailSerializer(UserListSerializer):

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + ["bio"]

class UserProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["id", "email", "username", "image", "bio"]
