from rest_framework import serializers

from main.models import User, Post, Topic, Board


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())

    class Meta:
        model = Post
        fields = ('topic', 'author', 'content')


class TopicSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    class Meta:
        model = Topic
        fields = ('board', 'author', 'content', 'title')


class AuxPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id',)


class AuxTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id',)

# from generic_relations.relations import GenericRelatedField
# class VoteSerializer(serializers.ModelSerializer):
#     voter = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     content_object = GenericRelatedField({
#         Topic: serializers.HyperlinkedRelatedField(
#             queryset=Topic.objects.all(),
#             view_name='topic-detail',
#         ),
#         Post: serializers.HyperlinkedRelatedField(
#             queryset=Post.objects.all(),
#             view_name='post-detail',
#         ),
#     })
#
#     class Meta:
#         model = Vote
#         fields = ('vote_type', 'voter', 'content_object')
