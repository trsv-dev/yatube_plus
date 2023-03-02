from django.urls import reverse_lazy
from django.views.generic import CreateView

# from django.conf import settings
# from django.core.mail import send_mail

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
    #
    # subject = 'Добро пожаловать на Yatube'
    # message = f'Привет, {user.username}. Cпасибо за регистрацию на Yatube.'
    # email_from = settings.EMAIL_HOST_USER
    # recipient_list = [user.email, ]
    # send_mail(subject, message, email_from, recipient_list)
