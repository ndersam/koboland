from django.db import models
from koboland import helpers
from main.models import User


class MessageThread(models.Model):
    hash_id = models.CharField(max_length=32, default=helpers.create_hash, unique=True)
    clients = models.ManyToManyField(User, blank=True)
    last_message = models.ForeignKey('Message', null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=64)

    def mark_read(self, user):
        UnreadReceipt.objects.filter(recipient=user, thread=self).delete()

    def add_message_text(self, text, sender):
        """User sends text to the chat
         - creates new message with foreign key to self
         - adds unread receipt for each user
         - returns instance of new message
        """
        new_message = Message.objects.create(text=text, sender=sender, thread=self)
        self.last_message = new_message
        self.save()
        for c in self.clients.exclude(id=sender.id):
            UnreadReceipt.objects.create(recipient=c, thread=self, message=new_message)
        return new_message


class Message(models.Model):
    hash_id = models.CharField(max_length=32, default=helpers.create_hash, unique=True)
    thread = models.ForeignKey(MessageThread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=1024)
    date = models.DateTimeField(db_index=True, auto_now_add=True)


class UnreadReceipt(models.Model):
    """
    Unread receipt for unread messages

    - Created for each recipient in a group chat when a message is sent.
    - Deleted when a user loads related thread or when they respond with
    the `read` flag over websocket connection.

    """
    date = models.DateTimeField(db_index=True, auto_now_add=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='receipts')
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='receipts')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipts')
