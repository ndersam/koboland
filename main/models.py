import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator
from django.db import IntegrityError
from django.db import models
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from commenting.utils import render_html
from main import model_fields
from .validators import UsernameValidator


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


class Votable(models.Model):
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
    flags = models.IntegerField(default=0)

    votes = GenericRelation('Vote')

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

    def generate_html(self):
        return render_html(self.content)

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


class Topic(Votable):
    title = models.CharField(max_length=80, validators=[MinLengthValidator(1)])
    slug = models.SlugField(max_length=48)
    author = models.ForeignKey('User', related_name='topics', on_delete=models.SET_NULL, null=True)
    board = models.ForeignKey('Board', related_name='topics', on_delete=models.CASCADE)
    is_closed = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)

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


class Post(Votable):
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
        page_size = getattr(settings, 'VOTABLE_PAGE_SIZE', 30)
        return self.topic.get_absolute_url() + f'?page={(self.topic.post_count // page_size) + 1}#{self.pseudoid}'


class VoteQuerySet(models.QuerySet):
    TYPE_TOPIC = 'topic'
    TYPE_POST = 'post'

    def on_topics(self):
        return self.filter(content_type__model='topic')

    def on_posts(self):
        return self.filter(content_type__model='post')

    def get_object(self, voter, votable_type, votable_id):
        return self.get(object_id=votable_id, voter=voter, content_type__model=votable_type)

    def create_object(self, user, votable=None, votable_type=None, votable_id=None, vote_type=None, is_shared=None):
        """
        Creates and returns a Vote object.
        Returns None if the following condition is satisfies:
            `(vote_type is None or vote_type == Vote.DIS_LIKE) and (is_shared is None or is_shared is False)`
        """
        kwargs = dict()

        if votable is None and (votable_id is None or votable_type is None):
            raise Exception('You must pass a `votable` or a combination of `votable_id` and `votable_type`')

        # No point storing vote that indicates `not-shared && NO_VOTE`
        if (vote_type is None or vote_type == Vote.NO_VOTE) and (is_shared is None or is_shared is False):
            return None

        if vote_type is not None:
            kwargs['vote_type'] = vote_type
        if is_shared is not None:
            kwargs['is_shared'] = is_shared

        if votable:
            content_object = votable
            votable_id = votable.id
        else:
            content_object = Topic.objects.get(id=votable_id) if votable_type == self.TYPE_TOPIC else Post.objects.get(
                id=votable_id)
        return self.create(object_id=votable_id, content_object=content_object, voter=user, **kwargs)


class Vote(models.Model):
    LIKE = 1
    DIS_LIKE = -1
    NO_VOTE = 0
    SHARE = 10
    VOTE_TYPES = (
        (LIKE, _("Like")), (DIS_LIKE, _("Dislike")), (NO_VOTE, _("NoVote")),
    )

    voter = models.ForeignKey('User', on_delete=models.PROTECT, null=True)
    vote_type = models.IntegerField(choices=VOTE_TYPES, null=False, default=NO_VOTE)
    vote_time = models.DateTimeField(auto_now_add=True)
    is_shared = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = VoteQuerySet.as_manager()

    class Meta:
        index_together = [
            ['content_type', 'object_id']
        ]

    def __str__(self):
        return f'{self.vote_type} - votable_type:{self.content_type}'

    def set_shared(self, is_shared):
        self.change_vote(new_share_status=is_shared)

    def change_vote(self, new_vote_type=None, new_share_status=None):
        votable = self.content_object

        if new_vote_type is not None:
            if self.vote_type == self.LIKE and new_vote_type == self.DIS_LIKE:
                votable.likes -= 1
                votable.dislikes += 1
            elif self.vote_type == self.LIKE and new_vote_type == self.NO_VOTE:
                votable.likes -= 1
            elif self.vote_type == self.DIS_LIKE and new_vote_type == self.LIKE:
                votable.likes += 1
                votable.dislikes -= 1
            elif self.vote_type == self.DIS_LIKE and new_vote_type == self.NO_VOTE:
                votable.dislikes -= 1
            elif self.vote_type == self.NO_VOTE and new_vote_type == self.LIKE:
                votable.likes += 1
            elif self.vote_type == self.NO_VOTE and new_vote_type == self.DIS_LIKE:
                votable.dislikes += 1
            self.vote_type = new_vote_type

        if new_share_status is not None:
            if self.is_shared is True and new_share_status is False:
                votable.shares -= 1
            elif self.is_shared is False and new_share_status is True:
                votable.shares += 1
            self.is_shared = new_share_status
        votable.save()
        if (self.vote_type is None or self.vote_type == self.NO_VOTE) and (
                self.is_shared is None or self.is_shared is False):
            self.delete()
        else:
            self.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # Initially created
        if not self.pk:
            votable = self.content_object
            if self.vote_type == self.LIKE:
                votable.likes += 1
            elif self.vote_type == self.DIS_LIKE:
                votable.dislikes += 1

            if self.is_shared:
                votable.shares += 1
            votable.save()
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        votable = self.content_object
        if self.vote_type == self.LIKE:
            votable.likes -= 1
        elif self.vote_type == self.DIS_LIKE:
            votable.dislikes -= 1

        if self.is_shared:
            votable.shares -= 1
        votable.save()
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
    # Copied from `AbstractUser` to change max_length, and Validator
    username_validator = UsernameValidator()
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
    topics_following = models.ManyToManyField('Topic', related_name='followers')
    followers = models.ManyToManyField('User', related_name='following')

    display_picture = models.OneToOneField(SubmissionMedia, on_delete=models.PROTECT, null=True)
    about_text = models.TextField(blank=True, null=True)
    reputation = models.IntegerField(default=0)
    objects = UserManager()
