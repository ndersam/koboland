from rest_framework import serializers

from chat.models import Message


class MessageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='hash_id', read_only=True)
    sender_id = serializers.CharField(source='sender.username', read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    thread_id = serializers.CharField(source='thread.hash_id', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'date', 'text', 'sender_id', 'sender_name', 'thread_id')


class MessageListSerializer(serializers.ListSerializer):
    child = MessageSerializer()
    many = True
    allow_null = True
