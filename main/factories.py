import factory

from main import models


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


class VoteFactory(factory.django.DjangoModelFactory):
    pass

    class Meta:
        model = models.Vote


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Board

    name = 'testBoard'
