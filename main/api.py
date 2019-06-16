from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.validators import FileValidator
from .models import Post, Topic, Vote
from .serializers import TopicSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class PostVoteAPI(APIView):
    pass
    # queryset = PostVote.objects.all()
    #
    # permission_classes = (IsAuthenticated,)
    #
    # def get_object(self, user, post_id, vote_type):
    #     try:
    #         vote = PostVote.objects.get(user=user, post_id=post_id, vote_type=vote_type)
    #         return vote
    #     except PostVote.DoesNotExist:
    #         raise Http404
    #
    # def post(self, request, format=None):
    #     request.data['user'] = request.user.username
    #     serializer = PostVoteSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, format=None):
    #     self.get_object(request.user, request.data['post'], request.data['vote_type']).delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class VotableVoteAPI(APIView):
    queryset = Vote.objects.all()

    TOPIC = 'topic'
    POST = 'post'

    @classmethod
    def get_object(cls, user, votable_type, votable_id):
        try:
            content_object = Topic.objects.get(id=votable_id) if votable_type == cls.TOPIC else Post.objects.get(
                id=votable_id)
            content_type = ContentType.objects.get_for_model(content_object)
            return cls.queryset.get(object_id=votable_id, voter=user, content_type=content_type)
        except (Topic.DoesNotExist, Post.DoesNotExist, Vote.DoesNotExist) as e:
            print(e)
            raise e

    @classmethod
    def create_object(cls, user, votable_type, votable_id, vote_type=None, share_status=None):
        try:
            kwargs = dict()
            if vote_type is not None:
                kwargs['vote_type'] = vote_type
            if share_status is not None:
                kwargs['is_shared'] = share_status

            content_object = Topic.objects.get(id=votable_id) if votable_type == cls.TOPIC else Post.objects.get(
                id=votable_id)
            return cls.queryset.create(content_object=content_object, voter=user, **kwargs)
        except Exception:
            raise Http404

    def post(self, request, format=None):
        request.data['user'] = request.user.username
        print(request.data)
        try:
            vote = self.get_object(request.user, request.data['votable_type'], request.data['votable_id'])
            vote_type = request.data.get('vote_type')
            is_shared = request.data.get('is_shared')

            if vote_type is None and is_shared is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'error': 'Both `vote_type` and `is_shared` parameters are missing'})

            if vote_type is not None and vote_type == vote.vote_type:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Vote type exists'})
            print('Yayyy')
            vote.change_vote(request.data.get('vote_type'), request.data.get('is_shared'))
        except Vote.DoesNotExist:
            vote_type = request.data.get('vote_type')
            is_shared = request.data.get('is_shared')

            if vote_type is None and is_shared is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'error': 'Both `vote_type` and `is_shared` parameters are missing'})

            self.create_object(request.user, request.data['votable_type'], request.data['votable_id'],
                               request.data.get('vote_type'), request.data.get('is_shared'))
        except Exception as e:
            # print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})

        return Response(status.HTTP_201_CREATED)

        # serializer = VoteSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        try:
            self.get_object(request.user, request.data['votable_type'], request.data['votable_id']).delete()
        except Exception as e:
            return Http404({'errors': str(e)})
        return Response(status=status.HTTP_204_NO_CONTENT)


class TopicVoteAPI(APIView):
    pass
    # queryset = TopicVote.objects.all()

    # @staticmethod
    # def get_object(user, topic_id, vote_type):
    #     try:
    #         return TopicVote.objects.get(user=user, topic_id=topic_id, vote_type=vote_type)
    #     except:
    #         raise Http404
    #
    # def post(self, request, format=None):
    #     request.data['user'] = request.user.username
    #     serializer = TopicVoteSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, format=None):
    #     self.get_object(request.user, request.data['topic'], request.data['vote_type']).delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class PostCreateAPI(APIView):
    file_validator = FileValidator(content_types=(getattr(settings, 'SUBMISSION_MEDIA_TYPES', '')))
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)

    # def post(self, request, format=None):
    #     data = request.POST.copy()
    #     data['author'] = request.user.username
    #     serializer = self.serialize(data)
    #     if serializer.is_valid():
    #         files = request.FILES.getlist('files')
    #
    #         try:
    #             self.validate_non_empty_post(data['content'], files)
    #         except ValidationError as e:
    #             return Response({'errors': e}, status=status.HTTP_400_BAD_REQUEST)
    #
    #         try:
    #             content_types = self.validate_files(files)
    #         except ValidationError as e:
    #             return Response({'errors': e}, status=status.HTTP_400_BAD_REQUEST)
    #
    #         submission = serializer.save()
    #         for file, content_type in zip(files, content_types):
    #             submission.files.create(file=file, content_type=content_type)
    #         return HttpResponseRedirect(submission.get_absolute_url())
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def validate_files(self, files):
    #     """ Validates files and returns a list of content_type of each file """
    #     content_types = []
    #     errors = []
    #     for file in files:
    #         try:
    #             # returns a dict containing content_type
    #             meta = self.file_validator(file)
    #             content_types.append(meta['content_type'])
    #         except ValidationError as e:
    #             errors += e.messages
    #     if len(errors) > 0:
    #         raise ValidationError(errors)
    #     return content_types
    #
    # @staticmethod
    # def validate_non_empty_post(text_content: str, files):
    #     if len(text_content.strip()) == 0 and len(files) == 0:
    #         raise ValidationError('Empty post')
    #
    # @classmethod
    # def serialize(cls, data):
    #     return PostSerializer(data=data)


class TopicCreateAPI(PostCreateAPI):
    queryset = Topic.objects.all()
    permission_classes = (IsAuthenticated,)

    @classmethod
    def serialize(cls, data):
        return TopicSerializer(data=data)
