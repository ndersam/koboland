from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

import json
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

    def test_create_topic_and_follow_works(self):
        self.assertEquals(self.board.topics.count(), 0)
        resp = self.client.post(reverse('topic_create'), data={
            'board': self.board.name,
            'content': self.content,
            'title': self.title,
            'follow_topic': True,
        })
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.user.topics.count(), 1)
        self.assertEquals(self.user.topics_following.count(), 1)

    def test_create_topic_and_not_follow_works(self):
        self.assertEquals(self.board.topics.count(), 0)
        resp = self.client.post(reverse('topic_create'), data={
            'board': self.board.name,
            'content': self.content,
            'title': self.title,
            'follow_topic': False,
        })
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.board.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.board.topics.count(), 1)
        self.assertEquals(self.user.topics.count(), 1)
        self.assertEquals(self.user.topics_following.count(), 0)

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


class TestFollowTopicAPI(TestCase):
    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        self.board = factories.BoardFactory(name='testBoard')
        self.topic = factories.TopicFactory(board=self.board, title='This is my title', content='This is content')
        self.client.force_login(self.user)

    def test_follow_topic_works(self):
        self.assertEquals(self.user.topics_following.count(), 0)
        resp = self.client.post(reverse('follow_topic'), data={
            'follow': True,
            'topic': self.topic.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.topics_following.count(), 1)

    def test_unfollow_followed_topic_works(self):
        self.assertEquals(self.user.topics_following.count(), 0)
        self.client.post(reverse('follow_topic'), data={
            'follow': True,
            'topic': self.topic.id,
        }, content_type='application/json')
        self.assertEquals(self.user.topics_following.count(), 1)

        resp = self.client.post(reverse('follow_topic'), data={
            'follow': False,
            'topic': self.topic.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.topics_following.count(), 0)

    def test_follow_followed_topic_returns_400(self):
        self.assertEquals(self.user.topics_following.count(), 0)
        resp = self.client.post(reverse('follow_topic'), data={
            'follow': True,
            'topic': self.topic.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.topics_following.count(), 1)

        resp = self.client.post(reverse('follow_topic'), data={
            'follow': True,
            'topic': self.topic.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.user.topics_following.count(), 1)

    def test_unfollow_not_followed_topic_returns_400(self):
        self.assertEquals(self.user.topics_following.count(), 0)
        resp = self.client.post(reverse('follow_topic'), data={
            'follow': False,
            'topic': self.topic.id,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.user.topics_following.count(), 0)


class TestFollowUserAPI(TestCase):
    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        self.friend = factories.UserFactory(username='friendUser', email='random@email.com')
        self.client.force_login(self.user)

    def test_follow_user_works(self):
        self.assertEquals(self.user.following.count(), 0)
        resp = self.client.post(reverse('follow_user'), data={
            'follow': True,
            'user': self.friend.username,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.following.count(), 1)

    def test_unfollow_followed_user_works(self):
        self.assertEquals(self.user.following.count(), 0)
        self.client.post(reverse('follow_user'), data={
            'follow': True,
            'user': self.friend.username,
        }, content_type='application/json')
        self.assertEquals(self.user.following.count(), 1)

        resp = self.client.post(reverse('follow_user'), data={
            'follow': False,
            'user': self.friend.username,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.following.count(), 0)

    def test_follow_followed_user_returns_400(self):
        self.assertEquals(self.user.following.count(), 0)
        resp = self.client.post(reverse('follow_user'), data={
            'follow': True,
            'user': self.friend.username,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.following.count(), 1)

        resp = self.client.post(reverse('follow_user'), data={
            'follow': True,
            'user': self.friend.username,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.user.following.count(), 1)

    def test_unfollow_not_followed_user_returns_400(self):
        self.assertEquals(self.user.following.count(), 0)
        resp = self.client.post(reverse('follow_user'), data={
            'follow': False,
            'user': self.friend.username,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.user.following.count(), 0)

    def test_follow_oneself_returns_400(self):
        self.assertEquals(self.user.following.count(), 0)
        resp = self.client.post(reverse('follow_user'), data={
            'follow': True,
            'user': self.user.username,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.user.following.count(), 0)

    def test_unfollow_oneself_returns_400(self):
        self.assertEquals(self.user.following.count(), 0)
        resp = self.client.post(reverse('follow_user'), data={
            'follow': False,
            'user': self.user.username,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.user.following.count(), 0)


class TestFollowBoardAPI(TestCase):
    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        self.board = factories.BoardFactory(name='testBoard')
        self.client.force_login(self.user)

    def test_follow_board_works(self):
        self.assertEquals(self.user.boards.count(), 0)
        resp = self.client.post(reverse('follow_board'), data={
            'follow': True,
            'board': self.board.name,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.boards.count(), 1)

    def test_unfollow_followed_board_works(self):
        self.assertEquals(self.user.boards.count(), 0)
        resp = self.client.post(reverse('follow_board'), data={
            'follow': True,
            'board': self.board.name,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.boards.count(), 1)

        resp = self.client.post(reverse('follow_board'), data={
            'follow': False,
            'board': self.board.name,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.boards.count(), 0)

    def test_follow_followed_board_returns_400(self):
        self.assertEquals(self.user.boards.count(), 0)
        resp = self.client.post(reverse('follow_board'), data={
            'follow': True,
            'board': self.board.name,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(self.user.boards.count(), 1)

        resp = self.client.post(reverse('follow_board'), data={
            'follow': True,
            'board': self.board.name,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.user.boards.count(), 1)

    def test_unfollow_not_followed_user_returns_400(self):
        self.assertEquals(self.user.boards.count(), 0)
        resp = self.client.post(reverse('follow_board'), data={
            'follow': False,
            'board': self.board.name,
        }, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.user.boards.count(), 0)


class TestPostUpdateAPI(TestCase):
    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        board = factories.BoardFactory(name='testBoard')
        self.topic = factories.TopicFactory(board=board, author=self.user, title='testTitle')
        self.p1 = factories.PostFactory(content='a', topic=self.topic, author=self.user)
        self.client.force_login(self.user)

    def test_update_post_without_file_works(self):
        content = 'b'
        resp = self.client.post(reverse('post_edit'), data={
            'votable_id': self.p1.id,
            'content': content,
            'files_to_keep': '{}',
        })
        self.p1.refresh_from_db()
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.assertEquals(content, self.p1.content)

    def test_update_post_by_emptying_fields_fails(self):
        resp = self.client.post(reverse('post_edit'), data={
            'votable_id': self.p1.id,
            'content': '',
            'files_to_keep': '{}',
        })
        self.p1.refresh_from_db()
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_post_by_faking_files_to_keep_fails(self):
        resp = self.client.post(reverse('post_edit'), data={
            'votable_id': self.p1.id,
            'content': self.p1.content,
            'files_to_keep': json.dumps({1: 2}),
        })
        self.p1.refresh_from_db()
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_post_by_another_user_fails(self):
        user2 = factories.UserFactory(username='user2', email='user2@mail.com')
        self.client.force_login(user2)
        resp = self.client.post(reverse('post_edit'), data={
            'votable_id': self.p1.id,
            'content': self.p1.content,
            'files_to_keep': json.dumps({}),
        })
        self.p1.refresh_from_db()
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_post_by_emptying_text_and_adding_file_works(self):
        self.assertEquals(self.p1.files.count(), 0)
        file = SimpleUploadedFile('in1.jpg', create_image(None, "main/sample_data/images/in1.jpg").getvalue())
        resp = self.client.post(reverse('post_edit'), {
            'votable_id': self.p1.id,
            'content': '',
            'files': [file],
            'files_to_keep': json.dumps({}),
        })
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.p1.refresh_from_db()
        self.assertEquals(self.p1.content, '')
        self.assertEquals(self.p1.files.count(), 1)

        files = self.p1.files.all()
        self.assertEquals(len(files), 1)
        for file in files:
            file.file.delete(save=False)

    def test_update_post_with_files_by_emptying_all_content_fails(self):
        file = factories.SubmissionMediaFactory()
        post = factories.PostFactory(content='a', topic=self.topic, author=self.user)
        post.files.add(file)
        post.save()
        post.refresh_from_db()

        self.assertEquals(post.files.count(), 1)

        resp = self.client.post(reverse('post_edit'), {
            'votable_id': post.id,
            'content': '',
            'files': [],
            'files_to_keep': json.dumps({}),
        })

        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        post.refresh_from_db()
        self.assertEquals(post.content, 'a')
        self.assertEquals(post.files.count(), 1)

        files = post.files.all()
        self.assertEquals(len(files), 1)
        for file in files:
            file.file.delete(save=False)

    def test_update_post_keeping_some_files_works(self):
        post = factories.PostFactory(content='a', topic=self.topic, author=self.user)
        post.files.add(factories.SubmissionMediaFactory())
        post.files.add(factories.SubmissionMediaFactory())
        post.save()
        post.refresh_from_db()

        self.assertEquals(post.files.count(), 2)

        name_of_kept = post.files.all()[1].file.name
        resp = self.client.post(reverse('post_edit'), {
            'votable_id': post.id,
            'content': 'a',
            'files': [],
            'files_to_keep': json.dumps({1: 0}),  # [keep first] ===> [Index in resulting file list]
        })

        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        post.refresh_from_db()
        self.assertEquals(post.content, 'a')
        self.assertEquals(post.files.count(), 1)
        self.assertEquals(post.files.first().file.name, name_of_kept)

        files = post.files.all()
        for file in files:
            file.file.delete(save=False)

    def test_update_post_keeping_some_files_works_2(self):
        """ Repeat of earlier test ... only keeping the first file in this case """
        post = factories.PostFactory(content='a', topic=self.topic, author=self.user)
        post.files.add(factories.SubmissionMediaFactory())
        post.files.add(factories.SubmissionMediaFactory())
        post.save()
        post.refresh_from_db()

        self.assertEquals(post.files.count(), 2)

        name_of_kept = post.files.all()[0].file.name
        resp = self.client.post(reverse('post_edit'), {
            'votable_id': post.id,
            'content': 'a',
            'files': [],
            'files_to_keep': json.dumps({0: 0}),  # [keep first] ===> [Index in resulting file list]
        })

        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        post.refresh_from_db()
        self.assertEquals(post.content, 'a')
        self.assertEquals(post.files.count(), 1)
        self.assertEquals(post.files.first().file.name, name_of_kept)

        files = post.files.all()
        for file in files:
            file.file.delete(save=False)


class TestTopicUpdateAPI(TestCase):
    def setUp(self) -> None:
        self.user = factories.UserFactory(username='testUser')
        self.board = factories.BoardFactory(name='testBoard')
        self.t1 = factories.TopicFactory(board=self.board, author=self.user, title='testTitle', content='a')
        self.client.force_login(self.user)

    def test_update_topic_without_file_works(self):
        content = 'b'
        title = 'newTitle'
        resp = self.client.post(reverse('topic_edit'), data={
            'votable_id': self.t1.id,
            'content': content,
            'title': title,
            'files_to_keep': '{}',
        })
        self.t1.refresh_from_db()
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.assertEquals(content, self.t1.content)
        self.assertEquals(title, self.t1.title)

    def test_update_topic_by_emptying_fields_fails(self):
        resp = self.client.post(reverse('topic_edit'), data={
            'votable_id': self.t1.id,
            'content': '',
            'title': '',
            'files_to_keep': '{}',
        })
        self.t1.refresh_from_db()
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_topic_by_faking_files_to_keep_fails(self):
        resp = self.client.post(reverse('topic_edit'), data={
            'votable_id': self.t1.id,
            'content': self.t1.content,
            'title': self.t1.title,
            'files_to_keep': json.dumps({1: 2}),
        })
        self.t1.refresh_from_db()
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_topic_by_another_user_fails(self):
        user2 = factories.UserFactory(username='user2', email='user2@mail.com')
        self.client.force_login(user2)
        resp = self.client.post(reverse('topic_edit'), data={
            'votable_id': self.t1.id,
            'content': self.t1.content,
            'title': self.t1.title,
            'files_to_keep': json.dumps({}),
        })
        self.t1.refresh_from_db()
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_topic_by_emptying_text_and_adding_file_works(self):
        self.assertEquals(self.t1.files.count(), 0)
        file = SimpleUploadedFile('in1.jpg', create_image(None, "main/sample_data/images/in1.jpg").getvalue())
        resp = self.client.post(reverse('topic_edit'), {
            'votable_id': self.t1.id,
            'content': '',
            'title': self.t1.title,
            'files': [file],
            'files_to_keep': json.dumps({}),
        })
        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        self.t1.refresh_from_db()
        self.assertEquals(self.t1.content, '')
        self.assertEquals(self.t1.files.count(), 1)

        files = self.t1.files.all()
        self.assertEquals(len(files), 1)
        for file in files:
            file.file.delete(save=False)

    def test_update_topic_with_files_by_emptying_all_content_fails(self):
        file = factories.SubmissionMediaFactory()
        topic = factories.TopicFactory(content='a', board=self.board, author=self.user)
        topic.files.add(file)
        topic.save()
        topic.refresh_from_db()

        self.assertEquals(topic.files.count(), 1)

        resp = self.client.post(reverse('topic_edit'), {
            'votable_id': topic.id,
            'content': '',
            'title': topic.title,
            'files': [],
            'files_to_keep': json.dumps({}),
        })

        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        topic.refresh_from_db()
        self.assertEquals(topic.content, 'a')
        self.assertEquals(topic.files.count(), 1)

        files = topic.files.all()
        self.assertEquals(len(files), 1)
        for file in files:
            file.file.delete(save=False)

    def test_update_post_keeping_some_files_works(self):
        topic = factories.TopicFactory(content='a', board=self.board, author=self.user)
        topic.files.add(factories.SubmissionMediaFactory())
        topic.files.add(factories.SubmissionMediaFactory())
        topic.save()
        topic.refresh_from_db()

        self.assertEquals(topic.files.count(), 2)

        name_of_kept = topic.files.all()[1].file.name
        resp = self.client.post(reverse('topic_edit'), {
            'votable_id': topic.id,
            'content': 'a',
            'title': topic.title,
            'files': [],
            'files_to_keep': json.dumps({1: 0}),  # [keep first] ===> [Index in resulting file list]
        })

        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        topic.refresh_from_db()
        self.assertEquals(topic.content, 'a')
        self.assertEquals(topic.files.count(), 1)
        self.assertEquals(topic.files.first().file.name, name_of_kept)

        files = topic.files.all()
        for file in files:
            file.file.delete(save=False)

    def test_update_post_keeping_some_files_works_2(self):
        """ Repeat of earlier test ... only keeping the first file in this case """
        topic = factories.TopicFactory(content='a', board=self.board, author=self.user)
        topic.files.add(factories.SubmissionMediaFactory())
        topic.files.add(factories.SubmissionMediaFactory())
        topic.save()
        topic.refresh_from_db()

        self.assertEquals(topic.files.count(), 2)

        name_of_kept = topic.files.all()[0].file.name
        resp = self.client.post(reverse('topic_edit'), {
            'votable_id': topic.id,
            'content': 'a',
            'title': topic.title,
            'files': [],
            'files_to_keep': json.dumps({0: 0}),  # [keep first] ===> [Index in resulting file list]
        })

        self.assertEquals(resp.status_code, status.HTTP_302_FOUND)
        topic.refresh_from_db()
        self.assertEquals(topic.content, 'a')
        self.assertEquals(topic.files.count(), 1)
        self.assertEquals(topic.files.first().file.name, name_of_kept)

        files = topic.files.all()
        for file in files:
            file.file.delete(save=False)