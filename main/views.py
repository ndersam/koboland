# Create your views here.
import logging

from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponseRedirect
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import UserCreationForm, PostCreateForm
from .models import Topic, Board, PostVote, TopicVote, Post
from .serializers import PostVoteSerializer, TopicVoteSerializer, PostSerializer

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
    ordering = ['-date_created']

    def get_queryset(self):
        self.topic = Topic.objects.get(id=self.kwargs['topic_id'])
        votes = self.topic.votes.filter(user=self.request.user)
        for vote in votes:
            if vote.vote_type == TopicVote.LIKE:
                self.topic.is_liked = True
            elif vote.vote_type == TopicVote.SHARE:
                self.topic.is_shared = True

        posts = self.topic.posts.all().prefetch_related('votes').order_by(*self.ordering)
        if self.request.user.is_authenticated:
            for post in posts:
                votes = post.votes.filter(user=self.request.user)
                for vote in votes:
                    if vote.vote_type == PostVote.LIKE:
                        post.is_liked = True
                    elif vote.vote_type == PostVote.SHARE:
                        post.is_shared = True
        return posts

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['topic'] = self.topic
        if self.request.user.is_authenticated:
            form = PostCreateForm(initial={'topic': self.topic, 'redirect': self.topic.get_absolute_url()},
                                  user=self.request.user)
            context['form'] = form
        return context


class TopicListView(ListView):
    paginate_by = 30
    template_name = 'main/topic_list.html'
    context_object_name = 'topics'
    ordering = ['date_created']

    def get_queryset(self):
        self.board = Board.objects.get(name=self.kwargs['board'])
        return self.board.topics.order_by(*self.ordering)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['board'] = self.board
        return context


class HomeListView(ListView):
    paginate_by = 30
    template_name = 'main/home.html'
    context_object_name = 'topics'
    ordering = ['date_created']

    def get_queryset(self):
        return Topic.objects.order_by(*self.ordering)


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


class PostCreateView(APIView):
    queryset = Post.objects.all()

    def post(self, request, format=None):
        redirect = request.data.pop('redirect')
        request.data['author'] = request.user.username
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponseRedirect(redirect)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PostCreateView(LoginRequiredMixin, CreateView):
#     template_name = 'main/post_create.html'
#     model = Post
#     queryset = Post.objects.all()
#     fields = ['content', 'topic']
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         return kwargs
#
#     def form_valid(self, form):
#         post: Post = form.save(commit=False)
#         post.author = self.request.user
#         post.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#     def get_success_url(self):
#         return self.request.POST['redirect']
