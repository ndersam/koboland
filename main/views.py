# Create your views here.
import logging

from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView

from .forms import UserCreationForm

logger = logging.getLogger(__name__)


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return self.request.GET.get('next', '/')

    def form_valid(self, form: UserCreationForm):
        response = super().form_valid(form)
        form.save()

        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(email=email, password=raw_password, username=username)

        login(self.request, user)
        form.send_mail()
        logger.info(f'New signup for email={email} && username={username}')
        return response
