from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from chat.models import MessageThread, Message
from chat.serializers import MessageListSerializer


@login_required
def load_inbox(request):
    """
    Load user inbox threads

    - Retrieve all of the threads that includes the user in the client field.
    - Count number of unread messages using related name receipts containing user
    - Returns {"threads": [thread]}
    :param request:
    :return:
    """
    threads = MessageThread.objects.filter(clients=request.user).annotate(
        unread_count=Count('receipts', filter=Q(receipts__recipient=request.user))
    )
    thread_data = MessageListSerializer(threads).data
    return JsonResponse({'threads': thread_data})


@login_required
def load_messages(request):
    """
    Load messages from thread

    - Load 30 messages by default
    - The `before` parameter will load the previous 30 messges
    relative to the date.
    - returns json {messages: [message], end:bool}
    :param request:
    :return:
    """
    thread = MessageThread.objects.get(hash_id=request.GET['id'])
    # make sure we are part of this chat before we read the messages
    if request.user not in thread.clients.all():
        return HttpResponse(status=403)
    # query for messages filter
    q = [Q(thread=thread)]
    if 'before' in request.GET:
        q.append(Q(date__lt=int(request.GET['before'])))
    # query messages matching filter
    messages = Message.objects.filter(*q).order_by('-id')
    messages_data = MessageListSerializer(messages[:30]).data
    # mark any unread messages in chat as read
    thread.mark_read(request.user)
    return JsonResponse({"messages": messages_data, "end": messages.count() <= 30})


@login_required
@csrf_exempt
def add_chatroom(request):
    """Add user to chatroom

         - create thread if existing one with title does not exist
         - user is added to the chat as well as the channel_layer group using the channel_name
           specified in the session.
        """
    title = request.POST['title'].strip()

    if MessageThread.objects.filter(title=title).exists():
        thread = MessageThread.objects.get(title=title)
    else:
        thread = MessageThread(title=title)
        thread.save()

    if request.user not in thread.clients.all():
        thread.clients.add(request.user)
    return HttpResponse(status=200)
