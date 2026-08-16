from rest_framework import serializers

from posts.models import Post, Comment, Hashtag


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "content", "image", "hashtags", "author", "created_at"]
        extra_kwargs = {
            "author": {
                "read_only": True,
            }
        }

class PostListSerializer(PostSerializer):
    likes = serializers.IntegerField(read_only=True)
    hashtags = serializers.SlugRelatedField(
        many=True, slug_field="name",
        queryset=Hashtag.objects.all()
    )
    author_username = serializers.CharField(source="author.username", read_only=True)
    count_comments = serializers.IntegerField(read_only=True)


    class Meta(PostSerializer.Meta):
        fields = ["id", "title", "image", "likes", "hashtags", "author_username", "count_comments", "created_at"]



class PostCreateUpdateSerializer(PostSerializer):
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        write_only=True
    )

    class Meta(PostSerializer.Meta):
        fields = ["id", "title", "content", "image", "hashtags"]


    @staticmethod
    def _get_or_create_hashtags(hashtag_data):
        hashtag_list = []
        for hashtag in hashtag_data:
            hashtag_obj, _ = Hashtag.objects.get_or_create(name=hashtag)
            hashtag_list.append(hashtag_obj)
        return hashtag_list


    def create(self, validated_data):
        hashtag_data = validated_data.pop("hashtags", [])
        post = Post.objects.create(**validated_data)
        hashtag_list = self._get_or_create_hashtags(hashtag_data)
        post.hashtags.add(
            *hashtag_list
        )
        return post


    def update(self, instance, validated_data):
        hashtag_data = validated_data.pop("hashtags", None)
        post = super().update(instance, validated_data)
        if hashtag_data is not None:
            hashtag_list = self._get_or_create_hashtags(hashtag_data)
            post.hashtags.set(
                hashtag_list
            )
        return post


class PostDetailSerializer(PostSerializer):
    hashtags = serializers.SlugRelatedField(slug_field="name", many=True, queryset=Hashtag.objects.all())
    author = serializers.CharField(source="author.username", read_only=True)



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "content", "author", "post", "created_at"]
        extra_kwargs = {
            "author": {
                "read_only": True
            },
            "post": {
                "read_only": True
            }
        }


class CommentListSerializer(CommentSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = ["id", "content", "author", "created_at"]


