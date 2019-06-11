# Create your views here.
import logging

from django.contrib.auth import authenticate, login
from django.http import Http404
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import UserCreationForm
from .models import Topic, Board, PostVote, TopicVote
from .serializers import PostVoteSerializer, TopicVoteSerializer

logger = logging.getLogger(__name__)


class SignupView(FormView):
    template_name = 'main/signup.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return self.request.GET.get('next', '/')

    def form_valid(self, form: UserCreationForm):
        response = super().form_valid(form)
        form.save()

        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(email=email, password=raw_password, username=username)

        login(self.request, user)
        form.send_mail()
        logger.info(f'New signup for email={email} && username={username}')
        return response


class PostListView(ListView):
    paginate_by = 30
    template_name = 'main/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.topic = Topic.objects.get(id=self.kwargs['topic_id'])
        posts = self.topic.posts.all().prefetch_related('votes')
        if self.request.user.is_authenticated:
            for post in posts:
                vote = post.votes.filter(user=self.request.user)
                if vote.count() > 0:
                    vote = vote.first()
                    post.is_liked = vote.vote_type == PostVote.LIKE
                    post.is_shared = vote.vote_type == PostVote.SHARE
        return posts

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['topic'] = self.topic
        return context


class TopicListView(ListView):
    paginate_by = 30
    template_name = 'main/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        self.board = Board.objects.get(name=self.kwargs['board'])
        return self.board.topics.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['board'] = self.board
        return context


class HomeListView(ListView):
    paginate_by = 30
    template_name = 'main/home.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.all()


class PostVoteView(APIView):
    queryset = PostVote.objects.all()

    @staticmethod
    def get_object(user, post_id, vote_type):
        try:
            return PostVote.objects.get(user=user, post_id=post_id, vote_type=vote_type)
        except:
            raise Http404

    def post(self, request, format=None):
        request.data['user'] = request.user.username
        serializer = PostVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        self.get_object(request.user, request.data['post'], request.data['vote_type']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TopicVoteView(APIView):
    queryset = TopicVote.objects.all()

    @staticmethod
    def get_object(user, topic_id, vote_type):
        try:
            return TopicVote.objects.get(user=user, topic_id=topic_id, vote_type=vote_type)
        except:
            raise Http404

    def post(self, request, format=None):
        request.data['user'] = request.user.username
        serializer = TopicVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        self.get_object(request.user, request.data['topic'], request.data['vote_type']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
