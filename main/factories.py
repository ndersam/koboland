import factory

from main import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topic

    title = 'This is a test title'
    slug = 'this-is-a-test-title'


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Post


class TopicVoteFactory(factory.django.DjangoModelFactory):
    pass
    # class Meta:
    #     model = models.TopicVote


class PostVoteFactory(factory.django.DjangoModelFactory):
    pass
    # class Meta:
    #     model = models.PostVote


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Board

    name = 'testBoard'
