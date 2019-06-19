from django.conf import settings
from django.core.validators import ValidationError
from django.http import Http404, HttpResponseRedirect
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.validators import FileValidator, VoteRequestValidator
from .models import Post, Topic, Vote
from .serializers import TopicSerializer, PostSerializer


class VotableVoteAPI(APIView):
    queryset = Vote.objects.all()
    validate_request = VoteRequestValidator()
    permission_classes = (IsAuthenticated,)
    TOPIC = 'topic'
    POST = 'post'

    LIKE = 1
    DISLIKE = -1
    NO_VOTE = 0
    SHARE = 2
    UNSHARE = -2

    @classmethod
    def get_object(cls, user, votable_type, votable_id):
        try:
            return Vote.objects.get_object(user, votable_type, votable_id)
        except (Topic.DoesNotExist, Post.DoesNotExist, Vote.DoesNotExist) as e:
            raise e

    @classmethod
    def create_object(cls, user, votable_type, votable_id, vote_type=None, is_shared=None):
        try:
            return Vote.objects.create_object(user, votable_type=votable_type, votable_id=votable_id,
                                              vote_type=vote_type, is_shared=is_shared)
        except Exception:
            raise Http404

    def post(self, request, format=None):
        request.data['voter'] = request.user.username

        # Map vote_type to `Model-compatible` representation
        vote_type = request.data.get('vote_type')
        is_shared = None
        if vote_type == self.SHARE or vote_type == self.UNSHARE:
            is_shared = vote_type == self.SHARE
            vote_type = None

        # Process request
        try:
            self.validate_request(request.data)
            vote = self.get_object(request.user, request.data['votable_type'], request.data['votable_id'])
            vote.change_vote(vote_type, is_shared)
        except Vote.DoesNotExist:
            self.create_object(request.user, request.data['votable_type'], request.data['votable_id'],
                               vote_type, is_shared)
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})

        return Response(status=status.HTTP_200_OK)


class PostCreateAPI(APIView):
    file_validator = FileValidator(content_types=(getattr(settings, 'SUBMISSION_MEDIA_TYPES', '')))
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        data = request.POST.copy()
        data['author'] = request.user.username
        serializer = self.serialize(data)
        if serializer.is_valid():
            files = request.FILES.getlist('files')

            try:
                self.validate_non_empty_post(data['content'], files)
            except ValidationError as e:
                return Response({'errors': e}, status=status.HTTP_400_BAD_REQUEST)

            try:
                content_types = self.validate_files(files)
            except ValidationError as e:
                return Response({'errors': e}, status=status.HTTP_400_BAD_REQUEST)

            submission = serializer.save()
            for file, content_type in zip(files, content_types):
                submission.files.create(file=file, content_type=content_type)
            return HttpResponseRedirect(submission.get_absolute_url())
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def validate_files(self, files):
        """ Validates files and returns a list of content_type of each file """
        content_types = []
        errors = []
        for file in files:
            try:
                # returns a dict containing content_type
                meta = self.file_validator(file)
                content_types.append(meta['content_type'])
            except ValidationError as e:
                errors += e.messages
        if len(errors) > 0:
            raise ValidationError(errors)
        return content_types

    @staticmethod
    def validate_non_empty_post(text_content: str, files):
        if len(text_content.strip()) == 0 and len(files) == 0:
            raise ValidationError('Empty post')

    @classmethod
    def serialize(cls, data):
        return PostSerializer(data=data)


class TopicCreateAPI(PostCreateAPI):
    queryset = Topic.objects.all()
    permission_classes = (IsAuthenticated,)

    @classmethod
    def serialize(cls, data):
        return TopicSerializer(data=data)
