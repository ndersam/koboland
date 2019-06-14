# Create your views here.
from django.http import Http404, HttpResponseRedirect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PostVote, TopicVote, Post
from .serializers import PostVoteSerializer, TopicVoteSerializer, PostSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class PostVoteView(APIView):
    queryset = PostVote.objects.all()

    permission_classes = (IsAuthenticated,)

    def get_object(self, user, post_id, vote_type):
        try:
            vote = PostVote.objects.get(user=user, post_id=post_id, vote_type=vote_type)
            return vote
        except PostVote.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        request.data['user'] = request.user.username
        serializer = PostVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
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
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        data = request.POST.copy()
        data['author'] = request.user.username
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()

            files = request.FILES.getlist('files')
            for file in files:
                post.files.create(file=file)
            return HttpResponseRedirect(post.get_absolute_url())
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
