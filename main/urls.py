from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from .forms import AuthenticationForm
from .views import (SignupView, PostListView, TopicListView, HomeListView,
                    PostVoteView)

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html', form_class=AuthenticationForm),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'~(?P<board>[A-Za-z0-9-_]+)/$', TopicListView.as_view(), name='board'),
    re_path(r'~(?P<board>[A-Za-z0-9-_]+)/(?P<topic_id>\d+)/(?P<topic_slug>[A-Za-z0-9-_]+)/$', PostListView.as_view(), name='topic'),
    path('api-auth/post/vote/', PostVoteView.as_view(), name='post_vote'),
]
