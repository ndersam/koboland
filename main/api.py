from django.conf import settings
from django.core.validators import ValidationError
from django.db.models import Manager
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.validators import FileValidator, VoteRequestValidator
from .models import Post, Topic, Vote, User, Board
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


class AbstractFollowAPI(APIView):
    permission_classes = (IsAuthenticated,)

    """
    Key that identifies a `followable`. 
    A `followable` is an item a user wises to follow.
        e.g 'user', 'topic' or 'board'
    """
    followable_key = None

    """
    Many-To-Many Field in `User` object to which a followable is added. 
        e.g. `topics_following` for `topic` ==> user.topics_following
             `boards` for `board` ==> user.boards
             `following` for `user` ==> user.following
    """
    follow_set_key = None

    """
    Primary key that identifies followable
    """
    primary_key = None

    ERRORS = {
        'missing': _('%s parameter not set'),
        'following': _('%s is already being followed.'),
        'user': _('User cannot follow oneself'),
    }

    def post(self, request, format=None):
        data = request.data
        data['follow'] = True if str(data.get('follow', True)).lower() == 'true' else False
        manager = self.get_object_manager()

        if self.followable_key is None:
            raise NotImplementedError(
                'Class `followable_key` attribute not set'
            )
        if self.follow_set_key is None:
            raise NotImplementedError(
                'Class `follow_set_key` attribute not set'
            )
        if self.primary_key is None:
            return NotImplementedError(
                'Class `primary_key` attribute not set'
            )

        if data[self.followable_key]:
            try:
                kwargs = {self.primary_key: data[self.followable_key]}
                followable = manager.get(**kwargs)
                follow_set = getattr(request.user, self.follow_set_key, None)

                if follow_set is None:
                    raise Exception(f'Illegal key `{self.follow_set_key}` on User object')

                # Prevent User from following himself/herself
                if isinstance(followable, User) and followable == request.user:
                    return Response({'errors': self.ERRORS['user']}, status=status.HTTP_400_BAD_REQUEST)

                existing = follow_set.filter(**kwargs)
                if len(existing) == 0 and data['follow']:
                    follow_set.add(followable)
                    return Response(status=status.HTTP_200_OK)
                elif len(existing) == 1 and not data['follow']:
                    follow_set.remove(followable)
                    return Response(status=status.HTTP_200_OK)

                errors = self.ERRORS['following'] % self.followable_key
            except Topic.DoesNotExist as e:
                errors = str(e)
        else:
            errors = self.ERRORS['missing'] % self.followable_key
        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def get_object_manager(cls) -> Manager:
        raise NotImplementedError(
            'You gotta implement this'
        )


class FollowTopicAPI(AbstractFollowAPI):
    queryset = Topic.objects.all()
    # permission_classes = FollowMixin.permission_classes
    followable_key = 'topic'
    follow_set_key = 'topics_following'
    primary_key = 'id'

    def get_object_manager(cls) -> Manager:
        return Topic.objects


class FollowUserAPI(AbstractFollowAPI):
    queryset = User.objects.all()
    followable_key = 'user'
    follow_set_key = 'following'
    primary_key = 'username'

    def get_object_manager(cls) -> Manager:
        return User.objects


class FollowBoardAPI(AbstractFollowAPI):
    queryset = Board.objects.all()
    followable_key = 'board'
    follow_set_key = 'boards'
    primary_key = 'name'

    def get_object_manager(cls) -> Manager:
        return Board.objects
