from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from main import factories
from main.api import VotableVoteAPI
from main.utils import create_image


class TestVoteAPI(TestCase):

    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        board = factories.BoardFactory(name='testBoard')
        topic = factories.TopicFactory(board=board, author=self.user, title='testTitle')
        self.post = factories.PostFactory(topic=topic, author=self.user)
        self.client.force_login(self.user)

    def test_like_post_works(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.LIKE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.likes, 1)
        self.assertEquals(self.post.votes.count(), 1)

    def test_dislike_post_works(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.DISLIKE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.dislikes, 1)
        self.assertEquals(self.post.votes.count(), 1)

    def test_share_post_works(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.SHARE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.shares, 1)
        self.assertEquals(self.post.votes.count(), 1)

    def test_unlike_liked_post_works(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.LIKE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.likes, 1)
        self.assertEquals(self.post.votes.count(), 1)

        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.NO_VOTE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.likes, 0)
        self.assertEquals(self.post.votes.count(), 0)

    def test_un_dislike_disliked_post_works(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.DISLIKE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.dislikes, 1)
        self.assertEquals(self.post.votes.count(), 1)

        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.NO_VOTE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.dislikes, 0)
        self.assertEquals(self.post.votes.count(), 0)

    def test_unshare_shared_post_works(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.SHARE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.shares, 1)
        self.assertEquals(self.post.votes.count(), 1)

        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.UNSHARE,
            'votable_id': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEquals(self.post.shares, 0)
        self.assertEquals(self.post.votes.count(), 0)

    def test_unlike_unliked_post_creates_nothing(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.NO_VOTE,
            'post': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.post.likes, 0)
        self.assertEquals(self.post.votes.count(), 0)

    def test_undislike_undisliked_post_creates_nothing(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.NO_VOTE,
            'post': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.post.dislikes, 0)
        self.assertEquals(self.post.votes.count(), 0)

    def test_unshare_unshared_post_creates_nothing(self):
        resp = self.client.post(reverse('votable_vote'), data={
            'vote_type': VotableVoteAPI.UNSHARE,
            'post': self.post.id,
            'votable_type': 'post',
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.post.shares, 0)
        self.assertEquals(self.post.votes.count(), 0)


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


class TestTopicCreateAPI(TestCase):
    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        self.board = factories.BoardFactory(name='testBoard')
        self.content = 'This is my content.'
        self.title = 'This is my title'
        self.client.force_login(self.user)

    def test_create_post_works_without_file(self):
        self.assertEquals(self.board.topics.count(), 0)
        resp = self.client.post(reverse('topic_create'), data={
            'board': self.board.name,
            'content': self.content,
            'title': self.title,
        })
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.user.topics.count(), 1)

    def test_create_post_works_with_one_file(self):

        file = SimpleUploadedFile('in1.jpg', create_image(None, "main/sample_data/images/in1.jpg").getvalue())
        self.assertEquals(self.board.topics.count(), 0)

        resp = self.client.post(reverse('topic_create'), {
            'board': self.board.name,
            'content': self.content,
            'title': self.title,
            'files': [file]
        })

        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.user.topics.count(), 1)

        files = self.board.topics.first().files.all()
        self.assertEquals(len(files), 1)
        for file in files:
            file.file.delete(save=False)

    def test_create_post_works_with_multiple_files(self):
        files = []
        for file in ['in1.jpg', 'in2.jpg']:
            files.append(
                SimpleUploadedFile(file,
                                   create_image(None, f"main/sample_data/images/{file}").getvalue())
            )

        self.assertEquals(self.board.topics.count(), 0)

        resp = self.client.post(reverse('topic_create'), {
            'board': self.board.name,
            'content': self.content,
            'title': self.title,
            'files': files
        })

        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.user.topics.count(), 1)

        files = self.board.topics.first().files.all()
        self.assertEquals(len(files), 2)
        for file in files:
            file.file.delete(save=False)

    def test_create_post_with_file_with_unsupported_file_format_returns_400(self):
        file = SimpleUploadedFile('front.png', b'this is some text - not an image')

        self.assertEquals(self.board.topics.count(), 0)

        resp = self.client.post(reverse('topic_create'), {
            'board': self.board.name,
            'content': self.content,
            'title': self.title,
            'files': [file]
        })

        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 0)
        self.assertEquals(self.board.topics.count(), 0)
        self.assertEquals(self.user.topics.count(), 0)

    def test_create_post_works_fails_with_empty_title(self):
        self.assertEquals(self.board.topics.count(), 0)
        resp = self.client.post(reverse('topic_create'), data={
            'board': self.board.name,
            'content': self.content,
            'title': '',
        })
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 0)
        self.assertEquals(self.board.topics.count(), 0)
        self.assertEquals(self.user.topics.count(), 0)

    def test_create_post_works_fails_with_both_files_and_text_empty(self):
        self.assertEquals(self.board.topics.count(), 0)
        resp = self.client.post(reverse('topic_create'), data={
            'board': self.board.name,
            'content': '',
            'title': self.title,
        })
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 0)
        self.assertEquals(self.board.topics.count(), 0)
        self.assertEquals(self.user.topics.count(), 0)

    def test_create_post_works_fails_with_empty_or_nonexistent_board_specified(self):
        self.assertEquals(self.board.topics.count(), 0)
        resp = self.client.post(reverse('topic_create'), data={
            'board': '',
            'content': self.content,
            'title': self.title,
        })
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 0)
        self.assertEquals(self.board.topics.count(), 0)
        self.assertEquals(self.user.topics.count(), 0)
