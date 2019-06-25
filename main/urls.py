from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from .api import (PostCreateAPI, TopicCreateAPI, VotableVoteAPI, FollowTopicAPI, FollowBoardAPI,
    FollowUserAPI, PostUpdateAPI, TopicUpdateAPI)
from .forms import AuthenticationForm
from .views import (SignupView, PostListView, TopicListView, HomeListView, PostUpdateView,TopicUpdateView,
                    TopicCreateView, logout_view, PostCreateView, UserView)

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html', form_class=AuthenticationForm),
         name='login'),
    path('logout/', logout_view, name='logout'),
    re_path(r'~(?P<board>[A-Za-z0-9-_]+)/$', TopicListView.as_view(), name='board'),
    re_path(r'~(?P<board>[A-Za-z0-9-_]+)/(?P<topic_id>[A-Za-z0-9-_]+)/(?P<topic_slug>[A-Za-z0-9-_]+)/$', PostListView.as_view(),
            name='topic'),
    path('api/vote/', VotableVoteAPI.as_view(), name='votable_vote'),
    path('api/post/add/', PostCreateAPI.as_view(), name='post_create'),
    path('api/topic/add/', TopicCreateAPI.as_view(), name='topic_create'),
    path('api/post/edit/', PostUpdateAPI.as_view(), name='post_edit'),
    path('api/topic/edit/', TopicUpdateAPI.as_view(), name='topic_edit'),
    path('api/topic/follow/', FollowTopicAPI.as_view(), name='follow_topic'),
    path('api/user/follow/', FollowUserAPI.as_view(), name='follow_user'),
    path('api/board/follow/', FollowBoardAPI.as_view(), name='follow_board'),
    path('topic/add/', TopicCreateView.as_view(), name='topic_create_view'),
    path('topic/edit/<slug:topic_id>/', TopicUpdateView.as_view(), name='topic-update-view'),
    path('post/add/', PostCreateView.as_view(), name='post_create_view'),
    path('post/edit/<slug:post_id>/', PostUpdateView.as_view(), name='post-update-view'),
    path('user/<slug:username>/', UserView.as_view(), name='user'),
]

if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
