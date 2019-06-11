from datetime import datetime, timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from main import factories, models
from main.models import Post, Topic


class TestModel(TestCase):

    def test_create_topic_sets_slug(self):
        author = factories.UserFactory()
        board = factories.BoardFactory()
        topic = models.Topic.objects.create(
            author=author, board=board, title='New Topic', content='This is content',
        )
        self.assertGreater(len(topic.slug), 0)

    def test_topic_modified_attribute_works_correctly(self):
        author = factories.UserFactory()
        board = factories.BoardFactory()
        topic = models.Topic.objects.create(
            author=author, board=board, title='New Topic', content='This is content',
        )
        self.assertFalse(topic.modified)
        topic.title = 'Updated Topic title'
        topic.save()
        self.assertTrue(topic.modified)

    def test_post_modified_attribute_works_correctly(self):
        author = factories.UserFactory()
        board = factories.BoardFactory()
        topic = factories.TopicFactory(board=board, author=author)
        post = models.Post.objects.create(
            author=author, topic=topic, content='This is content',
        )
        self.assertFalse(post.modified)
        post.content = 'Updated content'
        post.save()
        self.assertTrue(post.modified)

    def test_post_likes_works_correctly(self):
        user = factories.UserFactory()
        board = factories.BoardFactory()
        topic = factories.TopicFactory(board=board, author=user)
        post = factories.PostFactory(author=user, topic=topic)

        vote = models.PostVote.get_or_create(user, post, models.SubmissionVote.LIKE)
        self.assertEqual(vote.vote_type, models.SubmissionVote.LIKE)
        self.assertEqual(post.votes.count(), 1)
        self.assertEqual(post.likes, 1)
        self.assertEqual(user.post_votes.count(), 1)

    def test_post_shares_works_correctly(self):
        user = factories.UserFactory()
        board = factories.BoardFactory()
        topic = factories.TopicFactory(board=board, author=user)
        post = factories.PostFactory(author=user, topic=topic)

        vote = models.PostVote.get_or_create(user, post, models.SubmissionVote.SHARE)
        self.assertEqual(vote.vote_type, models.SubmissionVote.SHARE)
        self.assertEqual(post.votes.count(), 1)
        self.assertEqual(post.shares, 1)
        self.assertEqual(user.post_votes.count(), 1)

    def test_topic_likes_works_correctly(self):
        user = factories.UserFactory()
        board = factories.BoardFactory()
        topic = factories.TopicFactory(board=board, author=user)

        vote = models.TopicVote.get_or_create(user, topic, models.SubmissionVote.LIKE)
        self.assertEqual(vote.vote_type, models.SubmissionVote.LIKE)
        self.assertEqual(topic.votes.count(), 1)
        self.assertEqual(topic.likes, 1)
        self.assertEqual(user.topic_votes.count(), 1)

    def test_topic_shares_works_correctly(self):
        user = factories.UserFactory()
        board = factories.BoardFactory()
        topic = factories.TopicFactory(board=board, author=user)

        vote = models.TopicVote.get_or_create(user, topic, models.SubmissionVote.SHARE)
        self.assertEqual(vote.vote_type, models.SubmissionVote.SHARE)
        self.assertEqual(topic.votes.count(), 1)
        self.assertEqual(topic.shares, 1)
        self.assertEqual(user.topic_votes.count(), 1)


# noinspection PyArgumentList
class SubmissionTestCase(TestCase):

    def run_on_subclasses(func):
        classes = [Post, Topic]

        def _test_subclasses(self):
            for cls in classes:
                func(self, cls)

        return _test_subclasses

    @run_on_subclasses
    def test_how_long_0_seconds(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation
            self.assertEquals(post.how_long_ago(), '0 seconds ago')

    @run_on_subclasses
    def test_how_long_1_second(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(seconds=1)
            self.assertEquals(post.how_long_ago(), '1 second ago')

    @run_on_subclasses
    def test_how_long_multiple_second(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(seconds=42)
            self.assertEquals(post.how_long_ago(), '42 seconds ago')

    @run_on_subclasses
    def test_how_long_1_minute(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(minutes=1)
            self.assertEquals(post.how_long_ago(), '1 minute ago')

    @run_on_subclasses
    def test_how_long_multiple_minutes(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(minutes=42)
            self.assertEquals(post.how_long_ago(), '42 minutes ago')

    @run_on_subclasses
    def test_how_long_1_hour(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)

        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(hours=1)
            self.assertEqual(post.how_long_ago(), '1 hour ago')

    @run_on_subclasses
    def test_how_long_multiple_hours(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)

        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(hours=20)
            self.assertEqual(post.how_long_ago(), '20 hours ago')

    @run_on_subclasses
    def test_how_long_1_day(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(days=1)
            self.assertEqual(post.how_long_ago(), '1 day ago')

    @run_on_subclasses
    def test_how_long_multiple_days(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(days=20)
            self.assertEqual(post.how_long_ago(), '20 days ago')

    @run_on_subclasses
    def test_how_long_multiple_days_limit(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(days=20, hours=23, minutes=59, seconds=59)
            self.assertEqual(post.how_long_ago(), '20 days ago')

    @run_on_subclasses
    def test_how_long_multiple_hours_limit(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(hours=23, minutes=59, seconds=59)
            self.assertEqual(post.how_long_ago(), '23 hours ago')

    @run_on_subclasses
    def test_how_long_multiple_minutes_limit(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(minutes=59, seconds=59)
            self.assertEqual(post.how_long_ago(), '59 minutes ago')

    @run_on_subclasses
    def test_how_long_multiple_seconds_limit(self, cls):
        creation = datetime(year=1966, month=6, day=6, tzinfo=timezone.utc)
        post = cls(date_created=creation)
        with mock.patch('main.models.timezone') as dt:
            dt.now = mock.Mock()
            dt.now.return_value = creation + timedelta(seconds=59, milliseconds=999)
            self.assertEqual(post.how_long_ago(), '59 seconds ago')
