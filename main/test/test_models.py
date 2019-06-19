from datetime import datetime, timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from main import factories
from main.models import Post, Topic, Vote


class TestVote(TestCase):

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        board = factories.BoardFactory()
        self.topic = factories.TopicFactory(board=board, author=self.user, title='New Topic',
                                            content='This is content', )
        self.post = factories.PostFactory(author=self.user, topic=self.topic)

    def test_like_post_works_correctly(self):
        vote = Vote.objects.create_object(user=self.user, votable=self.post, vote_type=Vote.LIKE)
        self.assertEqual(vote.vote_type, Vote.LIKE)
        self.assertEqual(self.post.votes.count(), 1)
        self.assertEqual(self.post.likes, 1)
        self.assertEqual(self.user.vote_set.on_posts().count(), 1)

        vote.delete()
        self.assertEqual(self.post.votes.count(), 0)
        self.assertEqual(self.post.likes, 0)
        self.assertEqual(self.user.vote_set.on_posts().count(), 0)

    def test_dislike_post_works_correctly(self):
        vote = Vote.objects.create_object(user=self.user, votable=self.post, vote_type=Vote.DIS_LIKE)
        self.assertEqual(vote.vote_type, Vote.DIS_LIKE)
        self.assertEqual(self.post.votes.count(), 1)
        self.assertEqual(self.post.dislikes, 1)
        self.assertEqual(self.user.vote_set.on_posts().count(), 1)

        vote.delete()
        self.assertEqual(self.post.votes.count(), 0)
        self.assertEqual(self.post.dislikes, 0)
        self.assertEqual(self.user.vote_set.on_posts().count(), 0)

    def test_share_post_works_correctly(self):
        vote = Vote.objects.create_object(user=self.user, votable=self.post, is_shared=True)
        self.assertTrue(vote.is_shared)
        self.assertEquals(vote.vote_type, Vote.NO_VOTE)
        self.assertEqual(self.post.votes.count(), 1)
        self.assertEqual(self.post.shares, 1)
        self.assertEqual(self.user.vote_set.on_posts().count(), 1)

        vote.delete()
        self.assertEqual(self.post.votes.count(), 0)
        self.assertEqual(self.post.shares, 0)
        self.assertEqual(self.user.vote_set.on_posts().count(), 0)

    def test_like_topic_works_correctly(self):
        vote = Vote.objects.create_object(user=self.user, votable=self.topic, vote_type=Vote.LIKE)
        self.assertEqual(vote.vote_type, Vote.LIKE)
        self.assertEqual(self.topic.votes.count(), 1)
        self.assertEqual(self.topic.likes, 1)
        self.assertEqual(self.user.vote_set.on_topics().count(), 1)

        vote.delete()
        self.assertEqual(self.topic.votes.count(), 0)
        self.assertEqual(self.topic.likes, 0)
        self.assertEqual(self.user.vote_set.on_topics().count(), 0)

    def test_dislike_topic_works_correctly(self):
        vote = Vote.objects.create_object(user=self.user, votable=self.topic, vote_type=Vote.DIS_LIKE)
        self.assertEqual(vote.vote_type, Vote.DIS_LIKE)
        self.assertEqual(self.topic.votes.count(), 1)
        self.assertEqual(self.topic.dislikes, 1)
        self.assertEqual(self.user.vote_set.on_topics().count(), 1)

        vote.delete()
        self.assertEqual(self.topic.votes.count(), 0)
        self.assertEqual(self.topic.dislikes, 0)
        self.assertEqual(self.user.vote_set.on_topics().count(), 0)

    def test_share_topic_works_correctly(self):
        vote = Vote.objects.create_object(user=self.user, votable=self.topic, is_shared=True)
        self.assertTrue(vote.is_shared)
        self.assertEqual(vote.vote_type, Vote.NO_VOTE)
        self.assertEqual(self.topic.votes.count(), 1)
        self.assertEqual(self.topic.shares, 1)
        self.assertEqual(self.user.vote_set.on_topics().count(), 1)

        vote.delete()
        self.assertEqual(self.topic.votes.count(), 0)
        self.assertEqual(self.topic.shares, 0)
        self.assertEqual(self.user.vote_set.on_topics().count(), 0)

    # def test_post_shares_works_correctly(self):
    #     user = factories.UserFactory()
    #     board = factories.BoardFactory()
    #     topic = factories.TopicFactory(board=board, author=user)
    #     post = factories.PostFactory(author=user, topic=topic)
    #
    #     vote = models.PostVote.objects.create(user=user, post=post, vote_type=models.Vote.SHARE)
    #     self.assertEqual(vote.vote_type, models.Vote.SHARE)
    #     self.assertEqual(post.votes.count(), 1)
    #     self.assertEqual(post.shares, 1)
    #     self.assertEqual(user.post_votes.count(), 1)
    #
    #     vote.delete()
    #     self.assertEqual(post.votes.count(), 0)
    #     self.assertEqual(post.shares, 0)
    #     self.assertEqual(user.post_votes.count(), 0)
    #
    # def test_topic_likes_works_correctly(self):
    #     user = factories.UserFactory()
    #     board = factories.BoardFactory()
    #     topic = factories.TopicFactory(board=board, author=user)
    #
    #     vote = models.TopicVote.objects.create(user=user, topic=topic, vote_type=models.Vote.LIKE)
    #     self.assertEqual(vote.vote_type, models.Vote.LIKE)
    #     self.assertEqual(topic.votes.count(), 1)
    #     self.assertEqual(topic.likes, 1)
    #     self.assertEqual(user.topic_votes.count(), 1)
    #
    #     vote.delete()
    #     self.assertEqual(topic.votes.count(), 0)
    #     self.assertEqual(topic.likes, 0)
    #     self.assertEqual(user.topic_votes.count(), 0)
    #
    # def test_topic_shares_works_correctly(self):
    #     user = factories.UserFactory()
    #     board = factories.BoardFactory()
    #     topic = factories.TopicFactory(board=board, author=user)
    #
    #     vote = models.TopicVote.objects.create(user=user, topic=topic, vote_type=models.Vote.SHARE)
    #     self.assertEqual(vote.vote_type, models.Vote.SHARE)
    #     self.assertEqual(topic.votes.count(), 1)
    #     self.assertEqual(topic.shares, 1)
    #     self.assertEqual(user.topic_votes.count(), 1)
    #
    #     vote.delete()
    #     self.assertEqual(topic.votes.count(), 0)
    #     self.assertEqual(topic.shares, 0)
    #     self.assertEqual(user.topic_votes.count(), 0)
    #
    # def test_create_new_post_increases_topic_post_count(self):
    #     user = factories.UserFactory()
    #     board = factories.BoardFactory()
    #     topic = factories.TopicFactory(board=board, author=user)
    #
    #     self.assertEqual(topic.post_count, 0)
    #     factories.PostFactory(author=user, topic=topic)
    #     self.assertEqual(topic.post_count, 1)
    #
    # def test_delete_post_decreases_topic_post_count(self):
    #     user = factories.UserFactory()
    #     board = factories.BoardFactory()
    #     topic = factories.TopicFactory(board=board, author=user)
    #
    #     self.assertEqual(topic.post_count, 0)
    #     post = factories.PostFactory(author=user, topic=topic)
    #     self.assertEqual(topic.post_count, 1)
    #     post.delete()
    #     self.assertEqual(topic.post_count, 0)


class TestTopic(TestCase):

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        board = factories.BoardFactory()
        self.topic = factories.TopicFactory(board=board, author=self.user, title='New Topic',
                                            content='This is content', )

    def test_create_topic_sets_slug(self):
        self.assertGreater(len(self.topic.slug), 0)


class TestPost(TestCase):

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        board = factories.BoardFactory()
        self.topic = factories.TopicFactory(board=board, author=self.user, title='New Topic',
                                            content='This is content', )

    def test_new_post_increases_topic_post_count(self):
        self.assertEquals(self.topic.post_count, 0)
        factories.PostFactory(author=self.user, topic=self.topic)
        self.assertEquals(self.topic.post_count, 1)

    def test_delete_post_decreases_topic_post_count(self):
        self.assertEquals(self.topic.post_count, 0)
        post = factories.PostFactory(author=self.user, topic=self.topic)
        self.assertEquals(self.topic.post_count, 1)

        post.delete()
        self.assertEquals(self.topic.post_count, 0)
        self.assertEquals(self.topic.posts.count(), 0)


# noinspection PyArgumentList
class TestHowLongAgo(TestCase):

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
