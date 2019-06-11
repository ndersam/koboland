from rest_framework import serializers

from main import models


class PostVoteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.PostVote
        fields = ('is_up_vote', 'post', 'user')
