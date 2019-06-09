from unittest.mock import patch

from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from main import forms, models


class TestPage(TestCase):

    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
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
