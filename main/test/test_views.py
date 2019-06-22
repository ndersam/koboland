from unittest.mock import patch

from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from main import forms, models, factories


class TestAuthentication(TestCase):

    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/signup.html')
        self.assertContains(response, 'Koboland')
        self.assertIsInstance(response.context['form'], forms.UserCreationForm)

    def test_user_signup_page_submission_works(self):
        post_data = {
            'email': 'user@domain.com',
            'username': 'abracadabra',
            'password1': 'abcdabcdef',
        }
        with patch.object(forms.UserCreationForm, 'send_mail') as mock_send:
            response = self.client.post(reverse('signup'), post_data)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(models.User.objects.filter(email='user@domain.com').exists())
            self.assertTrue(auth.get_user(self.client).is_authenticated)
            mock_send.assert_called_once()

    def test_valid_login_form_redirects_to_home_page(self):
        cred = {
            'email': 'user@domain.com',
            'username': 'one_bad_boy',
            'password': 'abcabcabc',
        }
        models.User.objects.create_user(**cred)
        response = self.client.post(reverse('login'), data={
            'username': cred['username'],
            'password': cred['password']
        })
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        self.assertRedirects(response, reverse('home'))


class TestTopicPage(TestCase):

    def setUp(self) -> None:
        user = factories.UserFactory(username='testUser')
        board = factories.BoardFactory(name='testBoard')
        self.topic = factories.TopicFactory(board=board, author=user, title='testTitle')
        self.client.force_login(user)

    def test_topic_page_loads_correctly(self):
        resp = self.client.get(self.topic.get_absolute_url())
        self.assertIsInstance(resp.context['form'], forms.PostCreateForm)
        self.assertTemplateUsed(resp, 'main/post_list.html')

    def test_no_form_displayed_when_user_logged_out(self):
        self.client.logout()
        resp = self.client.get(reverse('home'))
        self.assertIsNone(resp.context.get('form'))


class TestTopicSubmitPage(TestCase):

    def test_topic_submit_page_loads_correctly(self):
        user = factories.UserFactory(username='testUser')
        self.client.force_login(user)
        resp = self.client.get(reverse('topic_create_view'))
        self.assertIsInstance(resp.context['form'], forms.TopicCreateForm)
        self.assertTemplateUsed(resp, 'main/topic_create.html')

    def test_topic_submit_page_requires_login(self):
        resp = self.client.get(reverse('topic_create_view'))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('topic_create_view')}")


class TestUserPage(TestCase):

    def test_user_page_loads_correctly(self):
        user = factories.UserFactory(username='testUser')
        self.client.force_login(user)
        resp = self.client.get(reverse('user', kwargs={'username': user.username}))
        self.assertTrue(resp.context['user_viewed'].is_me)
        self.assertTemplateUsed(resp, 'main/user.html')
