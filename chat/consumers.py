from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from main import models as user_models
from chat import models as chat_models
from . import serializers
from channels.db import database_sync_to_async

"""
Commands supported by ChatConsumer
----------------------------------

- CHAT_REQUEST: Send a request to have a direct one-on-one chat with a user that isnt'
    a friend (a user that isn't following the sender). The receiver of the request has
    to accept the request (by sending `ACCEPT_REQUEST`), before messages can be transferred.
    The receiver of the request can also reject the request by sending `DISMISS_REQUEST`.
- ACCEPT_REQUEST: Sent by a receiver of a `CHAT_REQUEST` to complete a kind of a "handshake"
    required to start communication.
- DISMISS_REQUEST: Sent by a receiver of a `CHAT_REQUEST` to ignore it. This implies that
   the (CHAT_REQUEST) request won't show up in the users list of chat requests.
   It won't be deleted from the database. A user who's request has been dismissed cannot sent another one. 

- JOIN_ROOM: Request to join a public room. 
- LEAVE_ROOM: Leave a public room.

- MESSAGE: Send a message to a "connected" user or group.
- READ: Mark a message as read.

- BLOCK_USER: Prevent a sender's message from reaching you. The sender, however, can continue
    sending his/her messages, but they won't be delivered.
"""

CHAT_REQUEST = 10
ACCEPT_REQUEST = 11
DISMISS_REQUEST = 12

JOIN_ROOM = 20
LEAVE_ROOM = 21
CREATE_ROOM = 22
DELETE_ROOM = 23
ADD_TO_ROOM = 24
REMOVE_FROM_ROOM = 25

MESSAGE = 30
READ = 31

BLOCK_USER = 40


class ChatConsumer(AsyncJsonWebsocketConsumer):

    @database_sync_to_async
    def get_threads(self):
        return chat_models.MessageThread.objects.filter(clients=self.scope['user'])

    @database_sync_to_async
    def get_thread(self, message_id):
        return chat_models.MessageThread.objects.get(hash_id=message_id, clients=self.scope['user'])

    async def connect(self):
        """
        User connects to socket

        - channel is added to each thread group they are included in.
        - channel_name is added to the session so that it can be referenced later in views.py
        """

        if self.scope['user'].is_authenticated:
            await self.accept()
            # add connection to existing channel groups
            threads = await self.get_threads()
            for thread in threads:
                await self.channel_layer.group_add(thread.hash_id, self.channel_name)
            # store client channel name in the user session
            self.scope['session']['channel_name'] = self.channel_name
            self.scope['session'].save()
        else:
            await self.close()

    async def disconnect(self, code):
        """
        User is disconnected

        - user will leave all groups and the channel name is removed from the session.
        :param code:
        :return:
        """
        if self.scope['user'].is_authenticated:
            if 'channel_name' in self.scope['session']:
                del self.scope['session']['channel_name']
                self.scope['session'].save()
            await self.channel_layer.group_discard(self.scope['user'].username, self.channel_name)

    async def receive_json(self, content, **kwargs):
        """
        User sends a message

        - read all messages if data is read message
        - send message to thread and group socket if text message
        - Message is sent to the group associated with the message thread
        """

        if 'read' in content:
            # client specifies they have read a message that was sent
            thread = chat_models.MessageThread.objects.get(hash_id=content['read'], clients=self.scope['user'])
            thread.mark_read(self.scope['user'])
        elif 'message' in content:
            message = content['message']
            # extra security is added when we specify clients=p
            thread = await self.get_thread(message['id'])
            # forward chat message over group channels
            new_message = await database_sync_to_async(thread.add_message_text)(message['text'], self.scope['user'])
            await self.channel_layer.group_send(
                thread.hash_id, {
                    'type': 'chat.message',
                    'message': serializers.MessageSerializer(new_message).data
                }
            )

    async def chat_message(self, event):
        """chat.message type"""
        message = event['message']
        await self.send_json(content=message)