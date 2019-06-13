from django.core import mail
from django.test import TestCase

from main import forms, factories


class TestForm(TestCase):

    def test_valid_signup_form_sends_email(self):
        form = forms.UserCreationForm(
            {
                'email': 'user@domain.com',
                'username': 'one_bad_boy',
                'password1': 'abcabcabc',
            }
        )
        self.assertTrue(form.is_valid())
        with self.assertLogs(forms.logger, level='INFO') as cm:
            form.send_mail()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Welcome to Koboland')
        self.assertGreaterEqual(len(cm.output), 1)


class TestPostCreateForm(TestCase):

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        board = factories.BoardFactory()
        self.topic = factories.TopicFactory(board=board, author=self.user)
        self.client.force_login(self.user)

    def test_post_create_form_works_correctly(self):
        form = forms.PostCreateForm(
            {
                'topic': self.topic.id,
                'content': 'Testing Testing...',
            },
            user=self.user
        )
        self.assertTrue(form.is_valid())

    def test_form_works_with_blank_content(self):
        form = forms.PostCreateForm({'topic': self.topic.id, 'content': ''}, user=self.user)
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_topic(self):
        form = forms.PostCreateForm({'topic': None, 'content': ''}, user=self.user)
        self.assertFalse(form.is_valid())

    def test_form_invalid_without_user(self):
        form = forms.PostCreateForm({'topic': None, 'content': ''}, user=None)
        self.assertFalse(form.is_valid())
