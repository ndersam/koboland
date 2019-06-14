# Create your views here.
from django.conf import settings
from django.core.validators import ValidationError
from django.http import Http404, HttpResponseRedirect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.validators import FileValidator
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
    validate_file = FileValidator(content_types=(getattr(settings, 'SUBMISSION_MEDIA_TYPES', '')))
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        data = request.POST.copy()
        data['author'] = request.user.username
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            files = request.FILES.getlist('files')
            content_types = []

            errors = []
            for file in files:
                try:
                    # returns a dict containing content_type
                    meta = self.validate_file(file)
                    content_types.append(meta['content_type'])
                except ValidationError as e:
                    errors += e.messages
            if len(errors) > 0:
                return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

            post = serializer.save()
            for file, content_type in zip(files, content_types):
                post.files.create(file=file, content_type=content_type)
            return HttpResponseRedirect(post.get_absolute_url())
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
