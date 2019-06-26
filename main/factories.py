import factory
from django.core.files import File
from main import models
from main.validators import FileValidator


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User
    username = 'testUser'


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topic

    title = 'This is a test title'
    slug = 'this-is-a-test-title'


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Post
    content = 'this is content'


class VoteFactory(factory.django.DjangoModelFactory):
    pass

    class Meta:
        model = models.Vote


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Board

    name = 'testBoard'


class SubmissionMediaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SubmissionMedia
    file = File(open("main/sample_data/images/in1.jpg", 'rb'))
    content_type = FileValidator()(file)['content_type']