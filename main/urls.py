from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from .forms import AuthenticationForm
from .views import SignupView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', form_class=AuthenticationForm),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('b/<slug:board>/<int:pk>/<slug:slug>/', TemplateView.as_view(template_name='home.html'), name='topic')
]
