import logging

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.core.mail import send_mail

from .models import User

logger = logging.getLogger(__name__)


class UserCreationForm(DjangoUserCreationForm):
    password2 = None

    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'password1')
        field_classes = {'username': UsernameField, 'email': forms.EmailField}

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            password_validation.validate_password(password1, self.instance)
        except forms.ValidationError as error:
            logger.info(error)
            # Method inherited from BaseForm
            self.add_error('password1', error)
        return password1

    def send_mail(self):
        logger.info(f'Sending verification email for email={self.cleaned_data["email"]}')
        message = f'Hi {self.cleaned_data["username"]},\nWelcome to the Koboland community.'
        'Please follow this link to verify your email.'
        send_mail('Welcome to Koboland',
                  message,
                  'koboland@koboland.com',
                  [self.cleaned_data['email']],
                  fail_silently=False
                  )
