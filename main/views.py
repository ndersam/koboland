# Create your views here.
import logging

from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import UserCreationForm
from .models import Topic, Board

logger = logging.getLogger(__name__)


class SignupView(FormView):
    template_name = 'signup.html'
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
    template_name = 'post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.topic = Topic.objects.get(id=self.kwargs['topic_id'])
        return self.topic.posts.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['topic'] = self.topic
        return context


class TopicListView(ListView):
    paginate_by = 30
    template_name = 'topic_list.html'
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
    template_name = 'home.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.all()
