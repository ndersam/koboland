from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from main import models, factories


class TestVoteAPI(TestCase):

    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        board = factories.BoardFactory(name='testBoard')
        topic = factories.TopicFactory(board=board, author=self.user, title='testTitle')
        self.post = factories.PostFactory(topic=topic, author=self.user)
        self.client.force_login(self.user)

    def test_like_post_works(self):
        resp = self.client.post(reverse('post_vote'), data={
            'vote_type': models.PostVote.LIKE,
            'post': self.post.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEquals(self.post.likes, 1)
        self.assertEquals(self.post.votes.count(), 1)

    def test_share_post_works(self):
        resp = self.client.post(reverse('post_vote'), data={
            'vote_type': models.PostVote.SHARE,
            'post': self.post.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEquals(self.post.shares, 1)
        self.assertEquals(self.post.votes.count(), 1)

    def test_unlike_liked_post_works(self):
        resp = self.client.post(reverse('post_vote'), data={
            'vote_type': models.PostVote.LIKE,
            'post': self.post.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEquals(self.post.likes, 1)
        self.assertEquals(self.post.votes.count(), 1)

        resp = self.client.delete(reverse('post_vote'), data={
            'vote_type': models.PostVote.LIKE,
            'post': self.post.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.post.refresh_from_db()
        self.assertEquals(self.post.likes, 0)
        self.assertEquals(self.post.votes.count(), 0)

    def test_unshare_shared_post_works(self):
        resp = self.client.post(reverse('post_vote'), data={
            'vote_type': models.PostVote.SHARE,
            'post': self.post.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEquals(self.post.shares, 1)
        self.assertEquals(self.post.votes.count(), 1)

        resp = self.client.delete(reverse('post_vote'), data={
            'vote_type': models.PostVote.SHARE,
            'post': self.post.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.post.refresh_from_db()
        self.assertEquals(self.post.shares, 0)
        self.assertEquals(self.post.votes.count(), 0)

    def test_like_unliked_post_returns_404(self):
        resp = self.client.delete(reverse('post_vote'), data={
            'vote_type': models.PostVote.LIKE,
            'post': self.post.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(self.post.likes, 0)

    def test_share_unshared_post_returns_404(self):
        resp = self.client.delete(reverse('post_vote'), data={
            'vote_type': models.PostVote.SHARE,
            'post': self.post.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(self.post.shares, 0)


class TestPostCreateAPI(TestCase):
    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        board = factories.BoardFactory(name='testBoard')
        self.topic = factories.TopicFactory(board=board, author=self.user, title='testTitle')
        self.client.force_login(self.user)

    def test_create_post_works(self):
        content = 'This is my content.'
        resp = self.client.post(reverse('post_create'), data={
            'topic': self.topic.id,
            'content': content,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.assertEquals(self.topic.post_count, 0)
        self.topic.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.topic.post_count, 1)
        self.assertEquals(self.topic.posts.count(), 1)
        self.assertEquals(self.user.posts.count(), 1)
