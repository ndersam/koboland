from django.test import TestCase

from main import factories, models


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
