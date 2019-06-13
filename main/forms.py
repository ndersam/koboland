import logging

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField, AuthenticationForm as DjangoAuthenticationForm
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from .models import User, Post, Topic

logger = logging.getLogger(__name__)


class UserCreationForm(DjangoUserCreationForm):
    """ This was subclassed to use only a single password. """
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


class AuthenticationForm(DjangoAuthenticationForm):
    """ Subclassed to change `invalid_login` message. """
    error_messages = {
        'invalid_login': _(
            "Invalid username/password combination"
        ),
        'inactive': _("This account is inactive."),
    }


class PostCreateForm(forms.ModelForm):
    redirect = forms.URLField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Post
        fields = ['content', 'topic']
        widgets = {
            'topic': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_topic(self):
        topic_id = self.cleaned_data['topic']
        try:
            Topic.objects.get(topic_id)
        except Topic.DoesNotExist:
            msg = f'{topic_id} does not exist'
            raise forms.ValidationError(_(msg), code='invalid')
        return topic_id
