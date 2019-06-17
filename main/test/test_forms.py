from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from main import forms, factories
from main.utils import create_image


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

    def test_post_create_form_works_correctly_without_files(self):
        form = forms.PostCreateForm(
            {
                'topic': self.topic.id,
                'content': 'Testing Testing...',
            },
            author=self.user
        )
        self.assertTrue(form.is_valid())

    def test_post_create_form_works_correctly_with_one_file(self):
        file = SimpleUploadedFile('in1.jpg', create_image(None, "main/sample_data/images/in1.jpg").getvalue())
        form = forms.PostCreateForm(
            {
                'topic': self.topic.id,
                'content': 'Testing Testing...',
                'files': file
            },
            author=self.user
        )
        self.assertTrue(form.is_valid())

    def test_form_works_with_blank_content(self):
        form = forms.PostCreateForm({'topic': self.topic.id, 'content': ''}, author=self.user)
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_topic(self):
        form = forms.PostCreateForm({'topic': None, 'content': ''}, author=self.user)
        self.assertFalse(form.is_valid())

    def test_form_invalid_without_user(self):
        form = forms.PostCreateForm({'topic': None, 'content': ''}, author=None)
        self.assertFalse(form.is_valid())
