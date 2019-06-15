import os
import uuid
from datetime import timedelta

import mistune
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import IntegrityError
from django.db import models
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

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
        return self.followers.count()

    def get_absolute_url(self):
        return reverse('board', kwargs={'board': self.name})


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('user_content', filename)


class SubmissionMedia(models.Model):
    # validate_file = FileValidator(content_types=(getattr(settings, 'SUBMISSION_MEDIA_TYPES', '')))
    file = models.FileField(upload_to=get_file_path)
    content_type = models.CharField(max_length=20)

    def is_image(self):
        return self.content_type.startswith('image')


class Submission(models.Model):
    content = models.TextField(blank=True)
    content_html = models.TextField(blank=True)
    modified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    pseudoid = models.CharField(default='', max_length=12, unique=True, editable=False)
    files = models.ManyToManyField('SubmissionMedia')

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    class Meta:
        abstract = True

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

    # TODO --> Use a `Renderer class` so as to simply testing
    def generate_html(self):
        return mistune.markdown(self.content)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.content_html = self.generate_html()

        if len(self.pseudoid) == 0:
            self.pseudoid = get_random_string()
        success = False
        failures = 0
        while not success:
            try:
                super().save(force_insert, force_update, using, update_fields)
            except IntegrityError as e:
                failures += 1
                if failures > 5:
                    raise e
                else:
                    self.pseudoid = get_random_string()
            else:
                success = True


class Topic(Submission):
    title = models.CharField(max_length=80, validators=[MinLengthValidator(1)])
    slug = models.SlugField(max_length=48)
    author = models.ForeignKey('User', related_name='topics', on_delete=models.SET_NULL, null=True)
    board = models.ForeignKey('Board', related_name='topics', on_delete=models.CASCADE)

    post_count = models.IntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        value = self.title
        # Only set the slug once ==> Updates not permitted
        # Initially, before the first save, this is None
        if not self.id:
            self.slug = slugify(value, allow_unicode=True)[:48]
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


class Post(Submission):
    author = models.ForeignKey('User', related_name='posts', on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey('Topic', related_name='posts', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id} - {self.author} - {self.content[:20]}...'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # Initially, before first save, this is None
        if self.id is None:
            self.topic.post_count += 1
            self.topic.save()
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

    # TODO ... fix this ... currently not working at all
    def delete(self, using=None, keep_parents=False):
        self.topic.post_count -= 1
        self.topic.save()
        super().delete(using, keep_parents)

    # TODO ....
    def get_absolute_url(self):
        return self.topic.get_absolute_url()


class SubmissionVote(models.Model):
    LIKE = 1
    SHARE = 2
    VOTE_TYPES = (
        (LIKE, _("Like")), (SHARE, _("Share")),
    )
    vote_type = models.IntegerField(choices=VOTE_TYPES, default=None, null=False)

    class Meta:
        abstract = True


class TopicVote(SubmissionVote):
    user = models.ForeignKey('User', related_name='topic_votes', on_delete=models.CASCADE)
    topic = models.ForeignKey('Topic', related_name='votes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'topic', 'vote_type')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.vote_type == self.LIKE:
            self.topic.likes += 1
        else:
            self.topic.shares += 1
        self.topic.save()
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.vote_type == self.LIKE:
            self.topic.likes += -1
        else:
            self.topic.shares += -1
        self.topic.save()
        super().delete(using, keep_parents)


class PostVote(SubmissionVote):
    user = models.ForeignKey('User', related_name='post_votes', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', related_name='votes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post', 'vote_type')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.vote_type == self.LIKE:
            self.post.likes += 1
        else:
            self.post.shares += 1
        self.post.save()
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.vote_type == self.LIKE:
            self.post.likes += -1
        else:
            self.post.shares += -1
        self.post.save()
        super().delete(using, keep_parents)


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
    # Copied from `AbstractUser` to change max_length
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=16,
        unique=True, primary_key=True,
        help_text=_('Required. 16 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    email = models.EmailField('email address', unique=True)
    is_banned = models.BooleanField(default=False)
    boards = models.ManyToManyField('Board', related_name='followers')

    about_text = models.TextField(blank=True, null=True)
    objects = UserManager()
