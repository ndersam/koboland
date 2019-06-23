from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, Exists, OuterRef
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from chat.models import MessageThread, Message
from chat.serializers import MessageListSerializer
from main.models import User


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


@login_required
def show_chat(request, friend_type, friend):
    if request.POST:
        raise Http404  # TODO

    new_thread = None
    if friend_type == 'user':
        kwargs = {'clients__username__in': [request.user.username, friend], 'thread_type': MessageThread.PRIVATE}
        annotation = {
            'display_name': ~Q('clients__username')
        }
    else:
        kwargs = {'name': friend, 'clients__username': request.user.username, }

    threads = MessageThread.objects.filter(
        clients=request.user
    ).annotate(
        last_message_date=F('last_message__date'),
        is_thread=Exists(
            MessageThread.objects.filter(id=OuterRef('id'), **kwargs))
    ).order_by('-is_thread', F('last_message_date').desc(nulls_last=True))

    if friend_type == 'user':
        if threads.exists() and threads.first().is_thread:  # matching thread, already exists
            setattr(threads.first(), 'display_name', friend)
        else:
            new_thread = MessageThread.objects.create(thread_type=MessageThread.PRIVATE)
            new_thread.clients.add(request.user)
            new_thread.clients.add(User.objects.get(username=friend))
            new_thread.save()
            setattr(new_thread, 'display_name', friend)

    print(threads, new_thread)

    return render(
        request, 'chat/room.html', {'threads': threads, 'new_thread': new_thread},
    )
