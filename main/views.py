# Create your views here.
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from commenting.utils import quote_votable
from .forms import UserCreationForm, PostCreateForm, TopicCreateForm
from .models import Topic, Board, Vote, Post

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
    ordering = ['date_created']

    def get_queryset(self):
        self.topic = Topic.objects.filter(id=self.kwargs['topic_id']).prefetch_related('files').first()
        if self.request.user.is_authenticated:
            votes = self.topic.votes.filter(voter=self.request.user)
            for vote in votes:
                if vote.vote_type in [Vote.LIKE, Vote.DIS_LIKE, Vote.NO_VOTE]:
                    self.topic.vote_type = vote.vote_type
                self.topic.is_shared = vote.is_shared

        posts = self.topic.posts.all().prefetch_related('votes', 'files').order_by(*self.ordering)
        if self.request.user.is_authenticated:
            for post in posts:
                votes = post.votes.filter(voter=self.request.user)
                for vote in votes:
                    if vote.vote_type in [Vote.LIKE, Vote.DIS_LIKE, Vote.NO_VOTE]:
                        post.vote_type = vote.vote_type
                    post.is_shared = vote.is_shared
        return posts

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['topic'] = self.topic
        if self.request.user.is_authenticated:
            form = PostCreateForm(initial={'topic': self.topic, 'redirect': self.topic.get_absolute_url()},
                                  author=self.request.user)
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


class TopicCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/topic_create.html'
    model = Topic
    queryset = Topic.objects.all()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['author'] = self.request.user
        if self.request.GET:
            board_name = self.request.GET.get('q', '')
            try:
                Board.objects.get(name=board_name)
                kwargs['board'] = board_name
            except Board.DoesNotExist:
                pass
        return kwargs

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        initial_board = kwargs.pop('board') if kwargs.get('board') else None
        form = TopicCreateForm(**kwargs)
        form.fields['board'].empty_label = _("Select board . . .")
        # TODO .... Fix this .. wrong capitalization fucks this
        if initial_board:
            form.fields['board'].initial = initial_board
        return form


def logout_view(request):
    logout(request)
    messages.info(
        request, "You've logged out successfully."
    )

    redirect = request.GET.get('next') or reverse('home')
    resp = HttpResponseRedirect(redirect)
    return resp


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/post_create.html'
    model = Post
    queryset = Topic.objects.all()

    def get_form_kwargs(self):
        self.topic = None
        kwargs = super().get_form_kwargs()
        kwargs['author'] = self.request.user
        if self.request.GET:
            topic_id = self.request.GET.get('topic')
            post_id = self.request.GET.get('post')
            should_quote_topic = self.request.GET.get('quote_topic')
            try:
                if topic_id:
                    self.topic = Topic.objects.get(id=topic_id)
                    kwargs['topic'] = topic_id
                if post_id:
                    post = Post.objects.get(id=post_id)
                    kwargs['post'] = quote_votable(post)
                if should_quote_topic and should_quote_topic == '1':
                    kwargs['post'] = quote_votable(self.topic)
            except (Topic.DoesNotExist, Post.DoesNotExist):
                pass
        return kwargs

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        topic = kwargs.pop('topic') if kwargs.get('topic') else None
        parent_post = kwargs.pop('post') if kwargs.get('post') else None
        kwargs['initial'].update({'topic': topic, 'content': parent_post})
        form = PostCreateForm(**kwargs)
        return form

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['topic'] = self.topic
        return kwargs

    def get(self, request, *args, **kwargs):
        resp = super().get(request, *args, **kwargs)
        if self.topic is None:
            raise Http404
        return resp
