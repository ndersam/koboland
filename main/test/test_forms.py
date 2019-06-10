from django.core import mail
from django.test import TestCase

from main import forms


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
