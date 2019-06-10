import factory

from main import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topic


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Post


class TopicVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TopicVote


class PostVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PostVote


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Board
