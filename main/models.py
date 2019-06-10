from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from main import model_fields


class Board(models.Model):
    # NEWEST = 10
    # MOST_VOTES = 20
    # MOST_COMMENTS = 30
    # BOARD_SORT = (
    #     (NEWEST, 'Newest'),
    #     (MOST_COMMENTS, 'Most Posts'),
    #     (MOST_VOTES, 'Most Votes'),
    # )

    name = model_fields.CICharField(max_length=32, primary_key=True)
    description = models.TextField(blank=True)
    moderators = models.ManyToManyField('User', related_name='moderates_on')

    def __str__(self):
        return self.name

    def follower_count(self):
        return self.followers().count()

    def get_absolute_url(self):
        return reverse('board', kwargs={'board': self.name})


class UserPostMixin:
    def up_votes(self) -> int:
        votes = self.votes
        return votes.filter(is_up_vote=True).count() if votes else 0

    def down_votes(self) -> int:
        votes = self.votes
        return votes.filter(is_up_vote=False).count() if votes else 0

    def points(self) -> int:
        return self.up_votes() - self.down_votes()

    def how_long_ago(self):
        how_long = timezone.now() - self.date_created
        if how_long < timedelta(minutes=1):
            return f'{how_long.seconds} second{pluralize(how_long.seconds)} ago'
        if how_long < timedelta(hours=1):
            minutes = how_long.seconds // 60
            return f'{minutes} minute{pluralize(minutes)} ago'
        if how_long < timedelta(days=1):
            hours = how_long.seconds // 3600
            return f'{hours} hour{pluralize(hours)} ago'
        return f'{how_long.days} day{pluralize(how_long.days)} ago'


class Topic(models.Model, UserPostMixin):
    title = models.CharField(max_length=80)
    slug = models.SlugField(max_length=48)
    author = models.ForeignKey('User', related_name='topics', on_delete=models.SET_NULL, null=True)
    board = models.ForeignKey('Board', related_name='topics', on_delete=models.CASCADE)
    content = models.TextField()
    modified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def set_vote(self, user, up_vote=True):
        TopicVote.objects.get_or_create(topic=self, user=user, is_up_vote=up_vote)

    def remove_vote(self, user):
        self.votes.filter(id=user.id).delete()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        value = self.title
        # Only set the slug once ==> Updates not permitted
        # Initially, before the first save, this is None
        if not self.id:
            self.slug = slugify(value, allow_unicode=True)[:48]
        else:
            self.modified = True
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

    def get_absolute_url(self):
        kwargs = {
            'topic_id': self.id,
            'topic_slug': self.slug,
            'board': self.board.name
        }
        return reverse('topic', kwargs=kwargs)

    def __str__(self):
        return self.title


class Post(models.Model, UserPostMixin):
    author = models.ForeignKey('User', related_name='posts', on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey('Topic', related_name='posts', on_delete=models.CASCADE)
    content = models.TextField()
    modified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.author} - {self.content[:20]}...'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # Initially, before the first save, this is None
        self.modified = self.id is not None
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)


class TopicVote(models.Model):
    user = models.ForeignKey('User', related_name='topic_votes', on_delete=models.CASCADE)
    is_up_vote = models.BooleanField(default=True)
    topic = models.ForeignKey('Topic', related_name='votes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'topic')


class PostVote(models.Model):
    user = models.ForeignKey('User', related_name='post_votes', on_delete=models.CASCADE)
    is_up_vote = models.BooleanField(default=True)
    post = models.ForeignKey('Post', related_name='votes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')


class UserManager(BaseUserManager):
    def _create_user(self, email, username, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )
        return self._create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    is_banned = models.BooleanField(default=False)
    boards = models.ManyToManyField('Board', related_name='followers')
    objects = UserManager()
