from django.urls import reverse_lazy
from django.views.generic import CreateView

from blog.forms import CustomUserForm


class AuthUserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserForm
    success_url = reverse_lazy('blog:index')
