from rest_framework import serializers

from main.models import PostVote, User, Post


class PostVoteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = PostVote
        fields = ('vote_type', 'post', 'user')
