from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Post, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'location',
            'category',
            'pub_date',
        )
        widgets = {'pub_date': forms.DateTimeInput({'type': 'datetime-local'})}

    def clean(self):
        super().clean()
        print("now " + str(timezone.now()))
        print("cleaned " + str(self.cleaned_data['pub_date']))
        if self.cleaned_data['pub_date'] < timezone.now():
            raise ValidationError(
                'Нельзя добавить запись в прошлом'
            )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )


class CustomUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта')

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )
