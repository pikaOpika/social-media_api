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


    class Meta(PostSerializer.Meta):
        fields = ["id", "title", "image", "likes", "hashtags", "author_username", "created_at"]



class PostCreateSerializer(PostSerializer):
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        write_only=True
    )

    class Meta(PostSerializer.Meta):
        fields = ["title", "content", "image", "hashtags"]

    def create(self, validated_data):
        hashtag_data = validated_data.pop("hashtags", [])
        post = Post.objects.create(**validated_data)
        hashtag_list = []
        for hashtag in hashtag_data:
            hashtag_obj, _ = Hashtag.objects.get_or_create(name=hashtag)
            hashtag_list.append(hashtag_obj)
        post.hashtags.add(
            *hashtag_list
        )
        return post
