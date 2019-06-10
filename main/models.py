from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Board(models.Model):
    name = models.CharField(max_length=32, primary_key=True)
    description = models.TextField(blank=True)
    moderators = models.ManyToManyField('User', related_name='moderates_on')

    def __str__(self):
        return self.name


class Topic(models.Model):
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
            'pk': self.id,
            'slug': self.slug,
            'board': self.board.name
        }
        return reverse('topic', kwargs=kwargs)

    def __str__(self):
        return self.title


class Post(models.Model):
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
