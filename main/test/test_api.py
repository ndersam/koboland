from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from main import models, factories
from main.utils import create_image


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

    def test_create_post_works_without_file(self):
        content = 'This is my content.'
        resp = self.client.post(reverse('post_create'), data={
            'topic': self.topic.id,
            'content': content,
        })
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.assertEquals(self.topic.post_count, 0)
        self.topic.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.topic.post_count, 1)
        self.assertEquals(self.topic.posts.count(), 1)
        self.assertEquals(self.user.posts.count(), 1)

    def test_create_post_works_with_one_file(self):
        content = 'This is my content.'
        file = SimpleUploadedFile('in1.jpg', create_image(None, "main/sample_data/images/in1.jpg").getvalue())
        resp = self.client.post(reverse('post_create'), {
            'topic': self.topic.id,
            'content': content,
            'files': [file]
        })
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.assertEquals(self.topic.post_count, 0)
        self.topic.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.topic.post_count, 1)
        self.assertEquals(self.topic.posts.count(), 1)
        self.assertEquals(self.user.posts.count(), 1)

        files = self.topic.posts.first().files.all()
        self.assertEquals(len(files), 1)
        for file in files:
            file.file.delete(save=False)

    def test_create_post_works_with_multiple_files(self):
        content = 'This is my content.'
        files = []
        for file in ['in1.jpg', 'in2.jpg']:
            files.append(
                SimpleUploadedFile(file,
                                   create_image(None, f"main/sample_data/images/{file}").getvalue())
            )
        resp = self.client.post(reverse('post_create'), {
            'topic': self.topic.id,
            'content': content,
            'files': files
        })
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.assertEquals(self.topic.post_count, 0)
        self.topic.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.topic.post_count, 1)
        self.assertEquals(self.topic.posts.count(), 1)
        self.assertEquals(self.user.posts.count(), 1)

        files = self.topic.posts.first().files.all()
        self.assertEquals(len(files), 2)
        for file in files:
            file.file.delete(save=False)

    def test_create_post_with_file_with_unsupported_file_format_returns_400(self):
        content = 'This is my content.'

        file = SimpleUploadedFile('front.png', b'this is some text - not an image')
        resp = self.client.post(reverse('post_create'), {
            'topic': self.topic.id,
            'content': content,
            'files': [file]
        })
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.topic.post_count, 0)
        self.topic.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.topic.post_count, 0)
        self.assertEquals(self.topic.posts.count(), 0)
        self.assertEquals(self.user.posts.count(), 0)
